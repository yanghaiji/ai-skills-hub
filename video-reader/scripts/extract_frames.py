#!/usr/bin/env python3
"""从视频中均匀抽取关键帧，输出 PNG 图片路径及对应时间点。

用法:
    python extract_frames.py <video_path> [--max-frames 8] [--interval N] [--output-dir DIR]

参数:
    --max-frames  最多抽取帧数，默认 8（未指定 interval 时按时长自动均匀分布）
    --interval    固定抽帧间隔（秒），指定后忽略 --max-frames
    --output-dir  帧图片输出目录，默认系统临时目录下的子目录

依赖: ffmpeg/ffprobe（缺失时可运行同目录 install_ffmpeg.py 自动安装）
"""

import argparse
import os
import subprocess
import sys
import tempfile

from ffmpeg_env import require_tools


def fail(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def get_duration(video_path: str, ffprobe: str) -> float:
    cmd = [
        ffprobe, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=60)
    if result.returncode != 0:
        fail(f"ffprobe 解析失败: {result.stderr.strip() or '文件不存在或格式不支持'}")
    try:
        return float(result.stdout.strip())
    except ValueError:
        fail("无法获取视频时长")
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="从视频抽取关键帧")
    parser.add_argument("video_path")
    parser.add_argument("--max-frames", type=int, default=8, help="最多抽取帧数，默认 8")
    parser.add_argument("--interval", type=float, default=0, help="固定抽帧间隔（秒），指定后忽略 --max-frames")
    parser.add_argument("--output-dir", default="", help="帧图片输出目录，默认系统临时目录")
    args = parser.parse_args()

    tools = require_tools("ffmpeg", "ffprobe")
    if not os.path.isfile(args.video_path):
        fail(f"视频文件不存在: {args.video_path}")

    duration = get_duration(args.video_path, tools["ffprobe"])
    if duration <= 0:
        fail("视频时长为 0 或无法读取")

    # 计算抽帧间隔：避开首尾黑帧，均匀分布
    if args.interval > 0:
        interval = args.interval
    else:
        n = max(1, min(args.max_frames, int(duration // 5) or 1))
        interval = duration / (n + 1)

    out_dir = args.output_dir or tempfile.mkdtemp(prefix="video_frames_")
    os.makedirs(out_dir, exist_ok=True)

    timestamps = []
    t = interval
    while t < duration and len(timestamps) < 64:
        timestamps.append(round(t, 2))
        t += interval

    frame_paths = []
    for i, ts in enumerate(timestamps, 1):
        out_file = os.path.join(out_dir, f"frame_{i:03d}_t{int(ts)}s.png")
        cmd = [
            tools["ffmpeg"], "-y", "-v", "error",
            "-ss", str(ts),
            "-i", args.video_path,
            "-frames:v", "1",
            "-vf", "scale='min(1280,iw)':-2",  # 宽度过大时压到 1280，节省分析开销
            out_file,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=120)
        if result.returncode == 0 and os.path.isfile(out_file):
            frame_paths.append((ts, out_file))
        else:
            print(f"[WARN] 时间点 {ts}s 抽帧失败: {result.stderr.strip()}", file=sys.stderr)

    if not frame_paths:
        fail("未成功抽取任何帧，请检查视频文件是否有效")

    print(f"视频时长: {duration:.1f}s | 抽帧间隔: {interval:.1f}s | 共 {len(frame_paths)} 帧")
    print(f"输出目录: {out_dir}")
    for ts, path in frame_paths:
        print(f"  [{ts:>8.1f}s] {path}")
    print("\n请用 Read 工具逐张读取以上 PNG 图片，分析画面内容（文字/图表/场景/操作）。")


if __name__ == "__main__":
    main()
