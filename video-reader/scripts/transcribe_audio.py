#!/usr/bin/env python3
"""视频语音转文字：ffmpeg 提取音轨 -> faster-whisper 转写，输出带时间戳的分段文本。

用法:
    python transcribe_audio.py <video_path> [--model small] [--language zh]
                               [--start 0] [--end 600] [--output result.txt]

参数:
    --model     whisper 模型: tiny | base | small | medium | large-v3，默认 small
                （首次运行会自动下载模型，需要联网；显存/内存不足时降级到 base/tiny）
    --language  语言提示，如 zh / en，不填则自动检测
    --start     仅转写该时间之后的内容（秒），默认从头
    --end       仅转写该时间之前的内容（秒），默认到尾
    --output    将转写结果保存到文件，默认打印到 stdout

依赖: ffmpeg（缺失时可运行同目录 install_ffmpeg.py 自动安装）；pip install faster-whisper
注意: 首次运行需下载 whisper 模型。默认走 hf-mirror.com 镜像（国内直连
      HuggingFace 通常超时）；已设置 HF_ENDPOINT 环境变量时以用户设置为准。
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from ffmpeg_env import require_tools


def fail(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def extract_audio(ffmpeg: str, video_path: str, wav_path: str, start: float, end: float) -> None:
    """提取音轨为 16kHz 单声道 WAV（whisper 输入格式）。"""
    cmd = [ffmpeg, "-y", "-v", "error"]
    if start > 0:
        cmd += ["-ss", str(start)]
    if end > start:
        cmd += ["-t", str(end - start)]
    cmd += ["-i", video_path, "-vn", "-ac", "1", "-ar", "16000", wav_path]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=3600)
    if result.returncode != 0 or not os.path.isfile(wav_path):
        fail(f"音频提取失败（视频可能无音轨）: {result.stderr.strip()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="视频语音转文字")
    parser.add_argument("video_path")
    parser.add_argument("--model", default="small",
                        help="tiny | base | small | medium | large-v3，默认 small")
    parser.add_argument("--language", default=None, help="语言提示，如 zh / en，默认自动检测")
    parser.add_argument("--start", type=float, default=0, help="起始时间（秒）")
    parser.add_argument("--end", type=float, default=0, help="结束时间（秒），0 表示到结尾")
    parser.add_argument("--output", default="", help="结果保存到文件")
    args = parser.parse_args()

    tools = require_tools("ffmpeg")
    if not os.path.isfile(args.video_path):
        fail(f"视频文件不存在: {args.video_path}")

    # 国内直连 HuggingFace 常超时，默认走镜像；用户已显式设置则尊重其配置
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        fail("未安装 faster-whisper，请执行: pip install faster-whisper")

    tmp_dir = tempfile.mkdtemp(prefix="video_audio_")
    wav_path = os.path.join(tmp_dir, "audio.wav")
    try:
        print(f"[INFO] 提取音轨中... ({fmt_time(args.start)} -> "
              f"{fmt_time(args.end) if args.end > 0 else '结尾'})", file=sys.stderr)
        extract_audio(tools["ffmpeg"], args.video_path, wav_path, args.start, args.end)

        print(f"[INFO] 加载 whisper 模型 '{args.model}'（来源: {os.environ['HF_ENDPOINT']}，首次运行需下载，请耐心等待）...", file=sys.stderr)
        try:
            try:
                model = WhisperModel(args.model, device="auto", compute_type="int8")
            except Exception:
                model = WhisperModel(args.model, device="cpu", compute_type="int8")
        except Exception as e:
            fail(f"模型加载/下载失败: {e}\n"
                 f"请检查网络，或手动指定其他镜像: set HF_ENDPOINT=<镜像地址>")

        segments, info = model.transcribe(wav_path, language=args.language, vad_filter=True)

        lines, full_text = [], []
        for seg in segments:
            text = seg.text.strip()
            if not text:
                continue
            offset = args.start
            lines.append(f"[{fmt_time(offset + seg.start)} -> {fmt_time(offset + seg.end)}] {text}")
            full_text.append(text)
            print(lines[-1], flush=True)  # 实时进度

        if not lines:
            fail("未识别到有效语音（视频可能无人声讲解），建议改用抽帧分析画面")

        result = (f"# 转写结果（检测语言: {info.language}, 置信度: {info.language_probability:.2f}）\n\n"
                  + "\n".join(lines) + "\n\n## 全文\n\n" + "".join(full_text))

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"\n[INFO] 已保存到: {args.output}", file=sys.stderr)
        else:
            print("\n" + result)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
