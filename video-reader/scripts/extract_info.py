#!/usr/bin/env python3
"""提取视频元信息（时长、分辨率、编解码、音轨），输出 JSON。

用法:
    python extract_info.py <video_path>

依赖: ffmpeg/ffprobe（缺失时可运行同目录 install_ffmpeg.py 自动安装）
"""

import json
import subprocess
import sys

from ffmpeg_env import require_tools


def fail(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("用法: python extract_info.py <video_path>")
    video_path = sys.argv[1]

    tools = require_tools("ffprobe")
    cmd = [
        tools["ffprobe"], "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams",
        video_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=60)
    except subprocess.TimeoutExpired:
        fail("ffprobe 执行超时")

    if result.returncode != 0:
        fail(f"ffprobe 解析失败: {result.stderr.strip() or '文件不存在或格式不支持'}")

    raw = json.loads(result.stdout)
    fmt = raw.get("format", {})

    info: dict = {
        "path": video_path,
        "duration_seconds": round(float(fmt.get("duration", 0)), 2),
        "size_mb": round(int(fmt.get("size", 0)) / 1024 / 1024, 2),
        "format_name": fmt.get("format_name", ""),
        "video_stream": None,
        "audio_stream": None,
    }

    for s in raw.get("streams", []):
        if s.get("codec_type") == "video" and info["video_stream"] is None:
            info["video_stream"] = {
                "codec": s.get("codec_name", ""),
                "width": s.get("width"),
                "height": s.get("height"),
                "fps": _parse_fps(s.get("r_frame_rate", "0/1")),
            }
        elif s.get("codec_type") == "audio" and info["audio_stream"] is None:
            info["audio_stream"] = {
                "codec": s.get("codec_name", ""),
                "language": s.get("tags", {}).get("language", "und"),
                "sample_rate": s.get("sample_rate"),
            }

    info["has_audio"] = info["audio_stream"] is not None
    print(json.dumps(info, ensure_ascii=False, indent=2))


def _parse_fps(fps_str: str) -> float:
    try:
        num, den = fps_str.split("/")
        return round(int(num) / int(den), 2) if int(den) else 0.0
    except (ValueError, ZeroDivisionError):
        return 0.0


if __name__ == "__main__":
    main()
