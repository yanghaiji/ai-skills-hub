#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行和报告生成模块
运行pytest测试并生成详细的测试报告
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


def check_pytest_installed() -> bool:
    """检查pytest是否已安装"""
    try:
        import pytest
        return True
    except ImportError:
        return False


def check_pytest_html_installed() -> bool:
    """检查pytest-html是否已安装"""
    try:
        import pytest_html
        return True
    except ImportError:
        return False


def install_pytest():
    """安装pytest及相关依赖"""
    print("正在安装pytest及相关依赖...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", 
                       "pytest", "pytest-html", "pytest-cov"], 
                      check=True, capture_output=True)
        print("✓ pytest安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ pytest安装失败: {e}")
        return False


def run_pytest(test_dir: str, report_path: str = None, 
               verbose: bool = True, coverage: bool = False) -> Dict[str, Any]:
    """
    运行pytest测试
    
    Args:
        test_dir: 测试目录
        report_path: 报告输出路径
        verbose: 是否显示详细输出
        coverage: 是否生成覆盖率报告
        
    Returns:
        测试结果字典
    """
    # 检查pytest-html是否安装
    if report_path and not check_pytest_html_installed():
        print("pytest-html未安装，正在安装...")
        if not install_pytest():
            return {"error": "pytest-html安装失败", "return_code": -1}
    
    # 构建pytest命令
    cmd = [sys.executable, "-m", "pytest", test_dir, "-v"]
    
    # 添加HTML报告选项
    if report_path:
        report_dir = Path(report_path).parent
        report_dir.mkdir(parents=True, exist_ok=True)
        cmd.extend(["--html", report_path, "--self-contained-html"])
    
    # 添加覆盖率选项
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html:coverage_report"])
    
    # 添加其他选项
    cmd.extend(["--tb=short", "-q"])
    
    print(f"运行测试命令: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        # 运行测试
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=test_dir)
        
        # 解析结果
        output = result.stdout + result.stderr
        
        # 提取测试结果信息
        test_result = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration": 0,
            "success_rate": 0,
            "output": output,
            "return_code": result.returncode
        }
        
        # 简单解析输出（实际应该更精确地解析）
        lines = output.split('\n')
        for line in lines:
            if "passed" in line:
                # 尝试提取数字
                import re
                numbers = re.findall(r'(\d+) passed', line)
                if numbers:
                    test_result["passed"] = int(numbers[0])
            elif "failed" in line:
                import re
                numbers = re.findall(r'(\d+) failed', line)
                if numbers:
                    test_result["failed"] = int(numbers[0])
            elif "skipped" in line:
                import re
                numbers = re.findall(r'(\d+) skipped', line)
                if numbers:
                    test_result["skipped"] = int(numbers[0])
            elif "error" in line.lower():
                import re
                numbers = re.findall(r'(\d+) error', line, re.IGNORECASE)
                if numbers:
                    test_result["errors"] = int(numbers[0])
        
        # 计算总数和成功率
        test_result["total"] = (test_result["passed"] + test_result["failed"] + 
                               test_result["skipped"] + test_result["errors"])
        if test_result["total"] > 0:
            test_result["success_rate"] = (
                test_result["passed"] / test_result["total"] * 100
            )
        
        return test_result
        
    except subprocess.TimeoutExpired:
        return {
            "error": "测试执行超时",
            "return_code": -1
        }
    except Exception as e:
        return {
            "error": f"测试执行失败: {str(e)}",
            "return_code": -1
        }


def generate_html_report(test_result: Dict[str, Any], 
                        test_cases_info: Dict[str, Any] = None,
                        output_path: str = "./test_report.html") -> None:
    """
    生成HTML测试报告
    
    Args:
        test_result: 测试结果
        test_cases_info: 测试用例信息
        output_path: 输出路径
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 计算成功率
    success_rate = test_result.get("success_rate", 0)
    if success_rate >= 90:
        status_color = "#4CAF50"  # 绿色
        status_text = "优秀"
    elif success_rate >= 70:
        status_color = "#FF9800"  # 橙色
        status_text = "良好"
    else:
        status_color = "#F44336"  # 红色
        status_text = "需改进"
    
    # 生成HTML内容
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .meta {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        .summary-card h3 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .summary-card p {{
            color: #666;
            font-size: 0.9em;
        }}
        .summary-card.success {{
            border-top: 4px solid #4CAF50;
        }}
        .summary-card.warning {{
            border-top: 4px solid #FF9800;
        }}
        .summary-card.error {{
            border-top: 4px solid #F44336;
        }}
        .summary-card.info {{
            border-top: 4px solid #2196F3;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            margin-top: 10px;
        }}
        .details {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }}
        .details h2 {{
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .output {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 20px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }}
        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>测试报告</h1>
            <div class="meta">
                <p>生成时间: {timestamp}</p>
                <p>测试目录: {test_result.get("test_dir", "N/A")}</p>
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card info">
                <h3>{test_result.get("total", 0)}</h3>
                <p>总测试用例</p>
            </div>
            <div class="summary-card success">
                <h3>{test_result.get("passed", 0)}</h3>
                <p>通过</p>
            </div>
            <div class="summary-card error">
                <h3>{test_result.get("failed", 0)}</h3>
                <p>失败</p>
            </div>
            <div class="summary-card warning">
                <h3>{test_result.get("skipped", 0)}</h3>
                <p>跳过</p>
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card" style="grid-column: span 2;">
                <h3 style="color: {status_color};">{success_rate:.1f}%</h3>
                <p>成功率</p>
                <span class="status-badge" style="background-color: {status_color};">
                    {status_text}
                </span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {success_rate}%; background-color: {status_color};"></div>
                </div>
            </div>
        </div>
        
        <div class="details">
            <h2>测试输出</h2>
            <div class="output">{test_result.get("output", "无输出")}</div>
        </div>
        
        <div class="details">
            <h2>测试详情</h2>
            <p><strong>执行时间:</strong> {test_result.get("duration", "N/A")} 秒</p>
            <p><strong>返回码:</strong> {test_result.get("return_code", "N/A")}</p>
            <p><strong>错误数:</strong> {test_result.get("errors", 0)}</p>
        </div>
        
        <div class="footer">
            <p>此报告由测试用例生成器自动生成</p>
        </div>
    </div>
</body>
</html>'''
    
    # 写入HTML文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ 测试报告已生成到: {output_path}")


def generate_json_report(test_result: Dict[str, Any], 
                        test_cases_info: Dict[str, Any] = None,
                        output_path: str = "./test_report.json") -> None:
    """
    生成JSON测试报告
    
    Args:
        test_result: 测试结果
        test_cases_info: 测试用例信息
        output_path: 输出路径
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": test_result,
        "test_cases_info": test_cases_info or {}
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON报告已生成到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='运行测试并生成报告')
    parser.add_argument('test_dir', help='测试代码目录')
    parser.add_argument('--report', '-r', default='./test_report.html', 
                       help='报告输出路径（默认: ./test_report.html）')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='显示详细输出')
    parser.add_argument('--coverage', '-c', action='store_true', 
                       help='生成覆盖率报告')
    parser.add_argument('--json', action='store_true', 
                       help='同时生成JSON格式报告')
    
    args = parser.parse_args()
    
    # 检查测试目录是否存在
    test_path = Path(args.test_dir)
    if not test_path.exists():
        print(f"✗ 测试目录不存在: {args.test_dir}")
        return 1
    
    # 检查pytest是否安装
    if not check_pytest_installed():
        if not install_pytest():
            return 1
    
    print(f"开始运行测试: {args.test_dir}")
    print("-" * 60)
    
    # 运行测试
    test_result = run_pytest(
        args.test_dir, 
        report_path=args.report,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    # 检查是否有错误
    if "error" in test_result:
        print(f"✗ 测试执行失败: {test_result['error']}")
        return 1
    
    # 生成报告
    print("-" * 60)
    print("测试执行完成，正在生成报告...")
    
    # 生成HTML报告
    generate_html_report(test_result, output_path=args.report)
    
    # 生成JSON报告（如果需要）
    if args.json:
        json_report_path = args.report.replace('.html', '.json')
        generate_json_report(test_result, output_path=json_report_path)
    
    # 显示结果摘要
    print("-" * 60)
    print("测试结果摘要:")
    print(f"  总测试用例: {test_result.get('total', 0)}")
    print(f"  通过: {test_result.get('passed', 0)}")
    print(f"  失败: {test_result.get('failed', 0)}")
    print(f"  跳过: {test_result.get('skipped', 0)}")
    print(f"  成功率: {test_result.get('success_rate', 0):.1f}%")
    
    if test_result.get('failed', 0) > 0:
        print("\n⚠ 有测试用例失败，请查看报告了解详情")
        return 1
    
    print("\n✓ 所有测试通过")
    return 0


if __name__ == '__main__':
    exit(main())
