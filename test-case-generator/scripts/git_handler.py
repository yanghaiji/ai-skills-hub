#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git操作处理模块
支持克隆、更新、切换分支/commit等操作
"""

import os
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple


def run_git_command(cmd: list, cwd: str = None) -> Tuple[bool, str]:
    """
    执行Git命令
    
    Args:
        cmd: Git命令列表
        cwd: 工作目录
        
    Returns:
        (成功标志, 输出信息)
    """
    try:
        result = subprocess.run(
            ['git'] + cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
            
    except subprocess.TimeoutExpired:
        return False, "Git命令执行超时"
    except FileNotFoundError:
        return False, "Git未安装或不在PATH中"


def check_git_installed() -> bool:
    """检查Git是否已安装"""
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False


def clone_repo(repo_url: str, target_dir: str, branch: str = None) -> Tuple[bool, str]:
    """
    克隆Git仓库
    
    Args:
        repo_url: 仓库地址
        target_dir: 目标目录
        branch: 分支名（可选）
        
    Returns:
        (成功标志, 仓库路径或错误信息)
    """
    target_path = Path(target_dir)
    
    # 如果目标目录已存在且是git仓库，尝试更新
    if target_path.exists() and (target_path / '.git').exists():
        print(f"  目标目录已存在，尝试更新: {target_path}")
        success, msg = update_repo(str(target_path))
        if success:
            return True, str(target_path)
        else:
            print(f"  更新失败: {msg}")
    
    # 创建目标目录
    target_path.mkdir(parents=True, exist_ok=True)
    
    # 构建克隆命令
    cmd = ['clone', repo_url]
    if branch:
        cmd.extend(['-b', branch])
    cmd.append(str(target_path))
    
    print(f"  正在克隆仓库: {repo_url}")
    success, msg = run_git_command(cmd)
    
    if success:
        print(f"  ✓ 仓库克隆成功: {target_path}")
        return True, str(target_path)
    else:
        print(f"  ✗ 克隆失败: {msg}")
        return False, msg


def update_repo(repo_dir: str) -> Tuple[bool, str]:
    """
    更新Git仓库（pull）
    
    Args:
        repo_dir: 仓库目录
        
    Returns:
        (成功标志, 输出信息)
    """
    if not (Path(repo_dir) / '.git').exists():
        return False, "目录不是Git仓库"
    
    print(f"  正在更新仓库...")
    success, msg = run_git_command(['pull'], cwd=repo_dir)
    
    if success:
        print(f"  ✓ 仓库更新成功")
        return True, msg
    else:
        print(f"  ✗ 更新失败: {msg}")
        return False, msg


def checkout(repo_dir: str, branch_or_commit: str) -> Tuple[bool, str]:
    """
    切换分支或commit
    
    Args:
        repo_dir: 仓库目录
        branch_or_commit: 分支名或commit hash
        
    Returns:
        (成功标志, 输出信息)
    """
    if not (Path(repo_dir) / '.git').exists():
        return False, "目录不是Git仓库"
    
    print(f"  正在切换到: {branch_or_commit}")
    
    # 先尝试作为本地分支切换
    success, msg = run_git_command(['checkout', branch_or_commit], cwd=repo_dir)
    
    if success:
        print(f"  ✓ 已切换到: {branch_or_commit}")
        return True, msg
    
    # 尝试创建并切换到新分支
    success, msg = run_git_command(['checkout', '-b', branch_or_commit], cwd=repo_dir)
    
    if success:
        print(f"  ✓ 已创建并切换到新分支: {branch_or_commit}")
        return True, msg
    
    # 尝试作为远程分支
    # 先fetch所有远程分支
    run_git_command(['fetch', '--all'], cwd=repo_dir)
    
    # 尝试切换到远程分支
    success, msg = run_git_command(['checkout', f'origin/{branch_or_commit}'], cwd=repo_dir)
    
    if success:
        # 创建本地分支跟踪远程分支
        run_git_command(['checkout', '-b', branch_or_commit, f'origin/{branch_or_commit}'], cwd=repo_dir)
        print(f"  ✓ 已切换到远程分支: {branch_or_commit}")
        return True, msg
    
    return False, f"无法切换到 {branch_or_commit}: {msg}"


def get_repo_info(repo_dir: str) -> Dict[str, str]:
    """
    获取仓库信息
    
    Args:
        repo_dir: 仓库目录
        
    Returns:
        仓库信息字典
    """
    info = {
        "current_branch": "",
        "commit_hash": "",
        "commit_message": "",
        "remote_url": "",
        "status": ""
    }
    
    if not (Path(repo_dir) / '.git').exists():
        return info
    
    # 获取当前分支
    success, branch = run_git_command(['branch', '--show-current'], cwd=repo_dir)
    if success:
        info["current_branch"] = branch
    
    # 获取当前commit hash
    success, hash_val = run_git_command(['rev-parse', '--short', 'HEAD'], cwd=repo_dir)
    if success:
        info["commit_hash"] = hash_val
    
    # 获取最新commit信息
    success, msg = run_git_command(['log', '-1', '--pretty=format:%s'], cwd=repo_dir)
    if success:
        info["commit_message"] = msg
    
    # 获取远程仓库地址
    success, url = run_git_command(['remote', 'get-url', 'origin'], cwd=repo_dir)
    if success:
        info["remote_url"] = url
    
    # 获取仓库状态
    success, status = run_git_command(['status', '--short'], cwd=repo_dir)
    if success:
        info["status"] = status if status else "clean"
    
    return info


def get_branches(repo_dir: str, include_remote: bool = True) -> list:
    """
    获取分支列表
    
    Args:
        repo_dir: 仓库目录
        include_remote: 是否包含远程分支
        
    Returns:
        分支名列表
    """
    branches = []
    
    # 获取本地分支
    success, output = run_git_command(['branch', '--list'], cwd=repo_dir)
    if success and output:
        for line in output.split('\n'):
            branch = line.strip().replace('* ', '')
            if branch:
                branches.append(branch)
    
    # 获取远程分支
    if include_remote:
        success, output = run_git_command(['branch', '-r', '--list'], cwd=repo_dir)
        if success and output:
            for line in output.split('\n'):
                branch = line.strip().replace('origin/', '')
                if branch and 'HEAD' not in branch and branch not in branches:
                    branches.append(branch)
    
    return branches


def get_commits(repo_dir: str, count: int = 10) -> list:
    """
    获取最近的commit列表
    
    Args:
        repo_dir: 仓库目录
        count: 获取数量
        
    Returns:
        commit列表 [{"hash": "xxx", "message": "xxx", "date": "xxx"}]
    """
    commits = []
    
    # 获取commit信息
    success, output = run_git_command(
        ['log', f'-{count}', '--pretty=format:%H|%s|%ai'],
        cwd=repo_dir
    )
    
    if success and output:
        for line in output.split('\n'):
            if '|' in line:
                parts = line.split('|', 2)
                if len(parts) >= 2:
                    commits.append({
                        "hash": parts[0][:8],
                        "full_hash": parts[0],
                        "message": parts[1],
                        "date": parts[2] if len(parts) > 2 else ""
                    })
    
    return commits


def main():
    parser = argparse.ArgumentParser(description='Git操作处理')
    parser.add_argument('action', choices=['clone', 'update', 'checkout', 'info', 'branches', 'commits'],
                       help='操作类型')
    parser.add_argument('--repo', help='仓库地址')
    parser.add_argument('--dir', help='仓库目录')
    parser.add_argument('--branch', help='分支或commit')
    parser.add_argument('--count', type=int, default=10, help='获取commit数量')
    
    args = parser.parse_args()
    
    # 检查Git是否安装
    if not check_git_installed():
        print("✗ Git未安装")
        return 1
    
    if args.action == 'clone':
        if not args.repo or not args.dir:
            print("✗ clone操作需要 --repo 和 --dir 参数")
            return 1
        success, result = clone_repo(args.repo, args.dir, args.branch)
        print(result if not success else f"✓ 仓库位置: {result}")
        
    elif args.action == 'update':
        if not args.dir:
            print("✗ update操作需要 --dir 参数")
            return 1
        success, msg = update_repo(args.dir)
        print(f"{'✓' if success else '✗'} {msg}")
        
    elif args.action == 'checkout':
        if not args.dir or not args.branch:
            print("✗ checkout操作需要 --dir 和 --branch 参数")
            return 1
        success, msg = checkout(args.dir, args.branch)
        print(f"{'✓' if success else '✗'} {msg}")
        
    elif args.action == 'info':
        if not args.dir:
            print("✗ info操作需要 --dir 参数")
            return 1
        info = get_repo_info(args.dir)
        print("\n仓库信息:")
        for key, value in info.items():
            print(f"  {key}: {value}")
            
    elif args.action == 'branches':
        if not args.dir:
            print("✗ branches操作需要 --dir 参数")
            return 1
        branches = get_branches(args.dir)
        print("\n分支列表:")
        for b in branches:
            print(f"  - {b}")
            
    elif args.action == 'commits':
        if not args.dir:
            print("✗ commits操作需要 --dir 参数")
            return 1
        commits = get_commits(args.dir, args.count)
        print(f"\n最近 {args.count} 条commit:")
        for c in commits:
            print(f"  {c['hash']} - {c['message']}")
    
    return 0


if __name__ == '__main__':
    exit(main())
