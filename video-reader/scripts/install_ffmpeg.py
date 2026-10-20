#!/usr/bin/env python3
"""自动安装 ffmpeg。

策略：
  - Windows: 优先 winget（Gyan.FFmpeg 全功能构建）
  - macOS:   brew install ffmpeg
  - 其他:    打印手动安装指引

安装完成后无需重启终端：ffmpeg_env 会兜底探测 winget/常见安装目录。
"""

import platform
import shutil
import subprocess
import sys

from ffmpeg_env import find_tool


def fail(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list) -> int:
    print(f"[INFO] 执行: {' '.join(cmd)}", file=sys.stderr)
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", timeout=1800).returncode
    except FileNotFoundError:
        return 127
    except subprocess.TimeoutExpired:
        fail("安装超时（>30 分钟），请检查网络后重试")
        return 1


def install_windows() -> None:
    winget = shutil.which("winget")
    if not winget:
        fail("未找到 winget。请手动安装 ffmpeg：https://www.gyan.dev/ffmpeg/builds/ "
             "（下载 full 版 zip，解压后将 bin 目录加入 PATH）")
    code = run([winget, "install", "--id", "Gyan.FFmpeg", "-e",
                "--accept-source-agreements", "--accept-package-agreements"])
    if code != 0 and not find_tool("ffmpeg"):
        fail(f"winget 安装失败（退出码 {code}）。请手动安装：https://www.gyan.dev/ffmpeg/builds/")


def install_macos() -> None:
    if not shutil.which("brew"):
        fail("未找到 Homebrew。请先安装 brew (https://brew.sh) 或手动下载 ffmpeg："
             "https://www.gyan.dev/ffmpeg/builds/")
    code = run(["brew", "install", "ffmpeg"])
    if code != 0 and not find_tool("ffmpeg"):
        fail(f"brew 安装失败（退出码 {code}），请检查网络后重试")


def main() -> None:
    if find_tool("ffmpeg") and find_tool("ffprobe"):
        print(f"[OK] ffmpeg 已安装，无需操作: {find_tool('ffmpeg')}")
        return

    system = platform.system()
    print("[INFO] 未检测到 ffmpeg，开始自动安装...", file=sys.stderr)
    if system == "Windows":
        install_windows()
    elif system == "Darwin":
        install_macos()
    else:
        fail("Linux 请使用系统包管理器安装，例如: sudo apt install ffmpeg")

    if find_tool("ffmpeg") and find_tool("ffprobe"):
        print(f"[OK] 安装成功: {find_tool('ffmpeg')}")
        print(f"[OK] ffprobe: {find_tool('ffprobe')}")
    else:
        fail("安装命令已执行但未探测到可执行文件，请重新打开终端后再试，或手动安装")


if __name__ == "__main__":
    main()
