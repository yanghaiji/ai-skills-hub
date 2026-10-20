#!/usr/bin/env python3
"""ffmpeg 工具定位共享模块。

查找顺序：PATH -> 常见安装目录兜底（winget Links / 手动安装目录 / homebrew）。
刚装完 ffmpeg 后当前终端的 PATH 可能未刷新，兜底目录可让脚本立即可用。
"""

import os
import shutil
import sys

IS_WINDOWS = os.name == "nt"
EXT = ".exe" if IS_WINDOWS else ""

# 常见安装位置（无需重启终端即可命中）
_EXTRA_DIRS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
    r"C:\ffmpeg\bin",
    os.path.expandvars(r"%ProgramFiles%\Gyan.FFmpeg"),
    "/usr/local/bin",
    "/opt/homebrew/bin",
]


def find_tool(name: str):
    """返回可执行文件绝对路径，找不到返回 None。"""
    path = shutil.which(name)
    if path:
        return path
    for d in _EXTRA_DIRS:
        if not d or "$" in d or "%" in d:  # 环境变量未解析则跳过
            continue
        cand = os.path.join(d, name + EXT)
        if os.path.isfile(cand):
            return cand
    return None


def require_tools(*names: str) -> dict:
    """确保工具可用，返回 {name: 绝对路径}；缺失时打印自动安装指引并退出。"""
    result, missing = {}, []
    for n in names:
        p = find_tool(n)
        if p:
            result[n] = p
        else:
            missing.append(n)
    if missing:
        installer = os.path.join(os.path.dirname(os.path.abspath(__file__)), "install_ffmpeg.py")
        print(f"[ERROR] 未找到 {'、'.join(missing)}（需要 ffmpeg 套件）", file=sys.stderr)
        print(f'[HINT] 自动安装（请先征得用户同意）: python "{installer}"', file=sys.stderr)
        print("[HINT] 或手动安装: https://www.gyan.dev/ffmpeg/builds/ 解压后将 bin 目录加入 PATH", file=sys.stderr)
        sys.exit(1)
    return result
