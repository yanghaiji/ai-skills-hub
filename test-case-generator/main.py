#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Case Generator - 主入口脚本
从需求文档自动生成测试用例、Python测试代码和测试报告
支持Git仓库集成
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# 添加scripts目录到路径
SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from parse_document import parse_document, format_content_for_ai
from generate_test_cases import generate_test_cases_from_content, generate_test_cases_json
from run_tests import run_pytest, generate_html_report, check_pytest_installed, install_pytest
from generate_test_case_excel import create_test_case_excel, check_openpyxl_installed, install_openpyxl
from git_handler import check_git_installed, clone_repo, update_repo, checkout, get_repo_info
from code_analyzer import CodeAnalyzer
from unified_test_generator import generate_unified_test_code
from xmind_generator import create_xmind_from_test_cases


def print_banner():
    """打印欢迎信息"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  Test Case Generator v5.6                   ║
║              从需求文档/代码自动生成测试用例                    ║
║                   支持 Git 仓库集成                          ║
╚══════════════════════════════════════════════════════════════╝
    """)


def load_output_config() -> dict:
    """
    加载输出配置
    
    配置优先级：
    1. 命令行参数
    2. 环境变量 TEST_CASE_OUTPUT
    3. 配置文件 .test-case-generator.json
    4. 默认值（全部生成）
    """
    config = {
        "generate_json": True,
        "generate_excel": True,
        "generate_xmind": True,
        "generate_code": True,
        "run_tests": True
    }
    
    # 尝试从环境变量读取
    env_output = os.environ.get("TEST_CASE_OUTPUT", "")
    if env_output:
        selections = [int(x.strip()) for x in env_output.split(",") if x.strip().isdigit()]
        if selections:
            config = {
                "generate_json": 1 in selections,
                "generate_excel": 2 in selections,
                "generate_xmind": 3 in selections,
                "generate_code": 4 in selections,
                "run_tests": 5 in selections
            }
            return config
    
    # 尝试从配置文件读取
    config_file = Path(".test-case-generator.json")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
                return config
        except Exception:
            pass
    
    return config  # 默认全部生成


def print_step(step: int, title: str):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"  Step {step}: {title}")
    print(f"{'='*60}")


def check_dependencies(include_git: bool = False) -> bool:
    """检查并安装依赖"""
    print("\n检查依赖...")
    
    # 检查python-docx
    try:
        import docx
        print("  ✓ python-docx 已安装")
    except ImportError:
        print("  ✗ python-docx 未安装，正在安装...")
        os.system(f"{sys.executable} -m pip install python-docx -q")
        try:
            import docx
            print("  ✓ python-docx 安装成功")
        except:
            print("  ✗ python-docx 安装失败")
            return False
    
    # 检查pdfplumber
    try:
        import pdfplumber
        print("  ✓ pdfplumber 已安装")
    except ImportError:
        print("  ✗ pdfplumber 未安装，正在安装...")
        os.system(f"{sys.executable} -m pip install pdfplumber -q")
        try:
            import pdfplumber
            print("  ✓ pdfplumber 安装成功")
        except:
            print("  ✗ pdfplumber 安装失败")
            return False
    
    # 检查pytest
    if not check_pytest_installed():
        print("  ✗ pytest 未安装，正在安装...")
        install_pytest()
    
    # 检查openpyxl
    if not check_openpyxl_installed():
        print("  ✗ openpyxl 未安装，正在安装...")
        install_openpyxl()
    
    # 检查Git（如果需要）
    if include_git:
        if check_git_installed():
            print("  ✓ Git 已安装")
        else:
            print("  ✗ Git 未安装或不在PATH中")
            return False
    
    print("\n✓ 所有依赖检查完成")
    return True


def run_pipeline_with_git(
    repo_url: str,
    branch_or_commit: str,
    doc_path: Optional[str],
    output_dir: str,
    skip_tests: bool = False,
    generate_excel: bool = True,
    generate_xmind: bool = True,
    generate_code: bool = True,
    keep_repo: bool = False
) -> dict:
    """
    运行Git仓库集成的完整流程
    
    Args:
        repo_url: Git仓库地址
        branch_or_commit: 分支名或commit hash
        doc_path: 需求文档路径（可选）
        output_dir: 输出目录
        skip_tests: 是否跳过测试运行
        generate_excel: 是否生成Excel文件
        keep_repo: 是否保留克隆的仓库
        
    Returns:
        执行结果字典
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = {
        "success": False,
        "files": {},
        "summary": {},
        "repo_info": {}
    }
    
    try:
        # Step 1: Git操作
        print_step(1, "Git操作 - 克隆/更新仓库")
        
        # 确定仓库本地目录
        repo_name = Path(repo_url).stem
        repo_dir = output_path / f"repo_{repo_name}_{timestamp}"
        
        # 克隆仓库
        success, result = clone_repo(repo_url, str(repo_dir), branch_or_commit)
        if not success:
            raise Exception(f"克隆仓库失败: {result}")
        
        # 切换到指定分支/commit（如果是新克隆的，可能已经切换了）
        if not (Path(result) / '.git').exists():
            success, msg = checkout(str(repo_dir), branch_or_commit)
            if not success:
                print(f"  ⚠ 切换分支警告: {msg}")
        
        # 获取仓库信息
        repo_info = get_repo_info(str(repo_dir))
        results["repo_info"] = repo_info
        
        print(f"\n  仓库信息:")
        print(f"    分支: {repo_info['current_branch']}")
        print(f"    Commit: {repo_info['commit_hash']}")
        print(f"    提交信息: {repo_info['commit_message']}")
        
        # Step 2: 代码分析
        print_step(2, "分析代码结构")
        
        analyzer = CodeAnalyzer(str(repo_dir))
        code_analysis = analyzer.analyze()
        print(analyzer.get_summary())
        
        results["code_analysis"] = {
            "language": code_analysis["language"],
            "test_framework": code_analysis["test_framework"],
            "existing_tests_count": len(code_analysis["existing_tests"])
        }
        
        # Step 3: 解析需求文档（如果提供）
        test_cases = []
        doc_title = ""
        if doc_path:
            print_step(3, "解析需求文档")
            print(f"  输入文件: {doc_path}")
            
            content = parse_document(doc_path)
            doc_title = content.get("title", "")
            formatted_content = format_content_for_ai(content)
            
            # 保存解析结果
            parsed_file = output_path / f"parsed_content_{timestamp}.json"
            with open(parsed_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            results["files"]["parsed_content"] = str(parsed_file)
            print(f"  ✓ 解析完成，保存到: {parsed_file}")
            
            # Step 4: 生成测试用例
            print_step(4, "生成测试用例")
            
            test_cases = generate_test_cases_from_content(content)
            test_cases_json_str = generate_test_cases_json(test_cases)
            test_cases_dicts = [tc.to_dict() for tc in test_cases]
            
            # 保存测试用例JSON
            test_cases_file = output_path / f"test_cases_{timestamp}.json"
            with open(test_cases_file, 'w', encoding='utf-8') as f:
                f.write(test_cases_json_str)
            
            results["files"]["test_cases_json"] = str(test_cases_file)
            results["summary"]["total_test_cases"] = len(test_cases)
            print(f"  ✓ 生成 {len(test_cases)} 个测试用例")
            print(f"  ✓ 保存到: {test_cases_file}")
        else:
            print_step(3, "基于代码生成测试用例")
            
            # 如果没有需求文档，基于代码结构生成测试用例
            test_cases_dicts = generate_test_cases_from_code(code_analysis, repo_dir)
            test_cases_json_str = json.dumps({"test_cases": test_cases_dicts}, ensure_ascii=False, indent=2)
            
            # 保存测试用例JSON
            test_cases_file = output_path / f"test_cases_{timestamp}.json"
            with open(test_cases_file, 'w', encoding='utf-8') as f:
                f.write(test_cases_json_str)
            
            results["files"]["test_cases_json"] = str(test_cases_file)
            results["summary"]["total_test_cases"] = len(test_cases_dicts)
            print(f"  ✓ 基于代码生成 {len(test_cases_dicts)} 个测试用例")
        
        # Step 5: 生成Excel测试用例
        if generate_excel and test_cases_dicts:
            print_step(5, "生成Excel测试用例")
            
            excel_file = output_path / f"test_cases_{timestamp}.xlsx"
            create_test_case_excel(test_cases_dicts, str(excel_file))
            
            results["files"]["test_cases_excel"] = str(excel_file)
            print(f"  ✓ Excel文件保存到: {excel_file}")
        
        # Step 5.1: 生成XMind思维导图
        if generate_xmind and test_cases_dicts:
            print_step(5, "生成XMind思维导图")
            
            xmind_file = output_path / f"test_cases_{timestamp}.xmind"
            create_xmind_from_test_cases(
                test_cases_dicts, 
                str(xmind_file),
                title=f"测试策略 - {timestamp}",
                doc_title=doc_title
            )
            
            results["files"]["test_cases_xmind"] = str(xmind_file)
            print(f"  ✓ XMind文件保存到: {xmind_file}")
        
        # Step 6: 生成测试代码
        if generate_code:
            test_code_dir = repo_dir / "generated_tests"
            print_step(6, "生成测试代码")
            
            # 确定项目类型和API信息
            language = code_analysis.get("language", "unknown")
            project_type = f"{language}"
            existing_tests = code_analysis.get("existing_tests", [])
            
            print(f"  项目类型: {project_type}")
            print(f"  已有测试文件: {len(existing_tests)} 个")
            
            # 使用统一测试代码生成器（无论什么项目都用Python测试）
            files = generate_unified_test_code(
                test_cases_dicts, 
                str(test_code_dir),
                project_type=project_type,
                base_url="http://localhost:8080",  # 默认值，用户可修改
                api_prefix="/api"
            )
            
            results["files"]["test_code_dir"] = str(test_code_dir)
            print(f"  ✓ 测试代码保存到: {test_code_dir}")
        
        # Step 7: 运行测试并生成报告
        if generate_code and not skip_tests:
            print_step(7, "运行测试并生成报告")
            
            report_file = output_path / f"test_report_{timestamp}.html"
            test_result = run_pytest(
                str(test_code_dir),
                report_path=str(report_file),
                verbose=True
            )
            
            results["files"]["test_report"] = str(report_file)
            results["summary"]["test_result"] = {
                "total": test_result.get("total", 0),
                "passed": test_result.get("passed", 0),
                "failed": test_result.get("failed", 0),
                "success_rate": test_result.get("success_rate", 0)
            }
            print(f"  ✓ 测试报告保存到: {report_file}")
        
        results["success"] = True
        
        # 打印完成摘要
        print(f"\n{'='*60}")
        print("  执行完成!")
        print(f"{'='*60}")
        print(f"\n  输出目录: {output_path}")
        print(f"\n  生成的文件:")
        for name, path in results["files"].items():
            print(f"    - {name}: {Path(path).name}")
        
        if results["summary"].get("test_result"):
            tr = results["summary"]["test_result"]
            print(f"\n  测试结果摘要:")
            print(f"    - 总测试用例: {tr['total']}")
            print(f"    - 通过: {tr['passed']}")
            print(f"    - 失败: {tr['failed']}")
            print(f"    - 成功率: {tr['success_rate']:.1f}%")
        
        # 清理仓库（如果不保留）
        if not keep_repo and repo_dir.exists():
            print(f"\n  正在清理临时仓库...")
            import shutil
            shutil.rmtree(repo_dir, ignore_errors=True)
        
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        results["error"] = str(e)
        import traceback
        traceback.print_exc()
    
    return results


def generate_test_cases_from_code(code_analysis: dict, repo_dir: Path) -> list:
    """
    基于代码分析结果生成测试用例
    
    Args:
        code_analysis: 代码分析结果
        repo_dir: 仓库目录
        
    Returns:
        测试用例字典列表
    """
    test_cases = []
    tc_id = 1
    
    # 获取已有测试作为参考
    existing_tests = code_analysis.get("existing_tests", [])
    if existing_tests:
        print(f"  发现 {len(existing_tests)} 个已有测试文件，将参考其风格")
    
    # 基于项目结构生成测试用例
    project_structure = code_analysis.get("project_structure", {})
    language = code_analysis.get("language", "unknown")
    test_framework = code_analysis.get("test_framework", "unknown")
    
    # 生成基础测试用例
    test_cases.append({
        "id": f"TC{tc_id:03d}",
        "name": f"项目基础功能测试",
        "description": f"验证{language}项目的基本功能，使用{test_framework}测试框架",
        "priority": "高",
        "test_type": "功能测试",
        "preconditions": ["项目已正确安装", "依赖已安装"],
        "steps": [
            f"1. 使用 {test_framework} 运行测试",
            "2. 验证所有测试通过",
            "3. 检查代码覆盖率"
        ],
        "expected_results": [
            "所有测试通过",
            "代码覆盖率达到预期",
            "无运行时错误"
        ]
    })
    tc_id += 1
    
    # 基于测试目录生成测试用例
    test_dirs = project_structure.get("test_dirs", [])
    if test_dirs:
        for test_dir in test_dirs:
            test_cases.append({
                "id": f"TC{tc_id:03d}",
                "name": f"{test_dir} 目录测试覆盖",
                "description": f"验证 {test_dir} 目录下的测试完整性",
                "priority": "中",
                "test_type": "功能测试",
                "preconditions": [f"{test_dir} 目录存在"],
                "steps": [
                    f"1. 扫描 {test_dir} 目录下的测试文件",
                    "2. 运行所有测试",
                    "3. 分析测试覆盖率"
                ],
                "expected_results": [
                    "测试文件结构合理",
                    "所有测试可执行",
                    "覆盖率满足要求"
                ]
            })
            tc_id += 1
    
    return test_cases


def run_pipeline(docx_path: str, 
                 output_dir: str = "./test_output",
                 skip_tests: bool = False,
                 generate_excel: bool = True,
                 generate_xmind: bool = True,
                 generate_code: bool = True) -> dict:
    """
    运行完整的测试生成流程（本地文档模式）
    
    Args:
        docx_path: 需求文档路径
        output_dir: 输出目录
        skip_tests: 是否跳过测试运行
        generate_excel: 是否生成Excel文件
        
    Returns:
        执行结果字典
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = {
        "success": False,
        "files": {},
        "summary": {}
    }
    
    try:
        # Step 1: 解析需求文档
        print_step(1, "解析需求文档")
        print(f"  输入文件: {docx_path}")
        
        content = parse_document(docx_path)
        formatted_content = format_content_for_ai(content)
        
        # 保存解析结果
        parsed_file = output_path / f"parsed_content_{timestamp}.json"
        with open(parsed_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        results["files"]["parsed_content"] = str(parsed_file)
        print(f"  ✓ 解析完成，保存到: {parsed_file}")
        
        # Step 2: 生成测试用例
        print_step(2, "生成测试用例")
        
        test_cases = generate_test_cases_from_content(content)
        test_cases_json_str = generate_test_cases_json(test_cases)
        
        # 将TestCase对象转换为字典列表（用于Excel生成）
        test_cases_dicts = [tc.to_dict() for tc in test_cases]
        
        # 保存测试用例JSON
        test_cases_file = output_path / f"test_cases_{timestamp}.json"
        with open(test_cases_file, 'w', encoding='utf-8') as f:
            f.write(test_cases_json_str)
        
        results["files"]["test_cases_json"] = str(test_cases_file)
        results["summary"]["total_test_cases"] = len(test_cases)
        print(f"  ✓ 生成 {len(test_cases)} 个测试用例")
        print(f"  ✓ 保存到: {test_cases_file}")
        
        # Step 3: 生成Excel测试用例
        if generate_excel:
            print_step(3, "生成Excel测试用例")
            
            excel_file = output_path / f"test_cases_{timestamp}.xlsx"
            create_test_case_excel(test_cases_dicts, str(excel_file))
            
            results["files"]["test_cases_excel"] = str(excel_file)
            print(f"  ✓ Excel文件保存到: {excel_file}")
        
        # Step 3.1: 生成XMind思维导图
        if generate_xmind:
            print_step(3, "生成XMind思维导图")
            
            xmind_file = output_path / f"test_cases_{timestamp}.xmind"
            doc_title = content.get("title", "")
            create_xmind_from_test_cases(
                test_cases_dicts, 
                str(xmind_file),
                title=f"测试策略 - {timestamp}",
                doc_title=doc_title
            )
            
            results["files"]["test_cases_xmind"] = str(xmind_file)
            print(f"  ✓ XMind文件保存到: {xmind_file}")
        
        # Step 4: 生成测试代码
        if generate_code:
            test_code_dir = output_path / f"generated_tests_{timestamp}"
            print_step(4, "生成测试代码")
            
            # 使用统一测试代码生成器
            files = generate_unified_test_code(
                test_cases_dicts, 
                str(test_code_dir),
                project_type="generic",
                base_url="http://localhost:8080",
                api_prefix="/api"
            )
            
            results["files"]["test_code_dir"] = str(test_code_dir)
            print(f"  ✓ 测试代码保存到: {test_code_dir}")
        
        # Step 5: 运行测试并生成报告
        if generate_code and not skip_tests:
            print_step(5, "运行测试并生成报告")
            
            report_file = output_path / f"test_report_{timestamp}.html"
            test_result = run_pytest(
                str(test_code_dir),
                report_path=str(report_file),
                verbose=True
            )
            
            results["files"]["test_report"] = str(report_file)
            results["summary"]["test_result"] = {
                "total": test_result.get("total", 0),
                "passed": test_result.get("passed", 0),
                "failed": test_result.get("failed", 0),
                "success_rate": test_result.get("success_rate", 0)
            }
            print(f"  ✓ 测试报告保存到: {report_file}")
        
        results["success"] = True
        
        # 打印完成摘要
        print(f"\n{'='*60}")
        print("  执行完成!")
        print(f"{'='*60}")
        print(f"\n  输出目录: {output_path}")
        print(f"\n  生成的文件:")
        for name, path in results["files"].items():
            print(f"    - {name}: {Path(path).name}")
        
        if results["summary"].get("test_result"):
            tr = results["summary"]["test_result"]
            print(f"\n  测试结果摘要:")
            print(f"    - 总测试用例: {tr['total']}")
            print(f"    - 通过: {tr['passed']}")
            print(f"    - 失败: {tr['failed']}")
            print(f"    - 成功率: {tr['success_rate']:.1f}%")
        
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        results["error"] = str(e)
        import traceback
        traceback.print_exc()
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Test Case Generator v5.6 - 从需求文档自动生成测试用例',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  # 模式1: 从需求文档生成（本地模式）
  python main.py --doc requirements.docx

  # 模式2: 从Git仓库生成（指定分支+需求文档）
  python main.py --repo https://github.com/user/project.git --branch feature/login --doc requirements.docx

  # 模式3: 从Git仓库生成（指定commit，无需求文档）
  python main.py --repo https://github.com/user/project.git --commit abc123

  # 指定输出目录
  python main.py --doc requirements.docx -o ./my_tests

  # 跳过测试运行
  python main.py --doc requirements.docx --skip-tests
        """
    )
    
    # 文档模式参数
    parser.add_argument('--doc', '-d', help='需求文档路径（支持 .docx, .pdf, .md, .txt）')
    
    # Git模式参数
    parser.add_argument('--repo', '-r', help='Git仓库地址')
    parser.add_argument('--branch', '-b', help='分支名')
    parser.add_argument('--commit', '-c', help='Commit hash')
    
    # 通用参数
    parser.add_argument('--output', '-o', default='./test_output', 
                       help='输出目录（默认: ./test_output）')
    parser.add_argument('--skip-tests', action='store_true',
                       help='跳过测试运行（只生成测试用例和代码）')
    parser.add_argument('--no-excel', action='store_true',
                       help='不生成Excel文件')
    parser.add_argument('--no-xmind', action='store_true',
                       help='不生成XMind思维导图')
    parser.add_argument('--no-code', action='store_true',
                       help='不生成Python测试代码')
    parser.add_argument('--only-json', action='store_true',
                       help='只生成JSON测试用例')
    parser.add_argument('--only-excel', action='store_true',
                       help='只生成Excel测试用例')
    parser.add_argument('--only-xmind', action='store_true',
                       help='只生成XMind思维导图')
    parser.add_argument('--keep-repo', action='store_true',
                       help='保留克隆的仓库（Git模式）')
    parser.add_argument('--check-deps', action='store_true',
                       help='只检查依赖，不执行生成')
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print_banner()
    
    # 检查参数
    has_repo = bool(args.repo)
    has_doc = bool(args.doc)
    
    if not has_repo and not has_doc:
        print("✗ 错误: 请至少提供 --doc（需求文档）或 --repo（Git仓库）参数")
        parser.print_help()
        return 1
    
    # 检查依赖
    if args.check_deps:
        check_dependencies(include_git=has_repo)
        return 0
    
    # 检查依赖
    if not check_dependencies(include_git=has_repo):
        print("\n✗ 依赖检查失败，请手动安装缺失的依赖")
        return 1
    
    # 如果没有指定任何输出选项，从配置加载
    if not (args.only_json or args.only_excel or args.only_xmind or 
            args.no_excel or args.no_xmind or args.no_code or args.skip_tests):
        # 从配置文件或环境变量加载
        output_options = load_output_config()
        
        # 将选择转换为命令行参数
        args.no_excel = not output_options["generate_excel"]
        args.no_xmind = not output_options["generate_xmind"]
        args.no_code = not output_options["generate_code"]
        args.skip_tests = not output_options["run_tests"]
        args.no_code = not output_options["generate_code"]
        args.skip_tests = not output_options["run_tests"]
    
    # 处理输出选项
    if args.only_json:
        # 只生成JSON
        args.no_excel = True
        args.no_xmind = True
        args.no_code = True
        args.skip_tests = True
    elif args.only_excel:
        # 只生成Excel
        args.no_xmind = True
        args.no_code = True
        args.skip_tests = True
    elif args.only_xmind:
        # 只生成XMind
        args.no_excel = True
        args.no_code = True
        args.skip_tests = True
    
    # 构建输出选项
    output_options = {
        "generate_excel": not args.no_excel,
        "generate_xmind": not args.no_xmind,
        "generate_code": not args.no_code,
        "skip_tests": args.skip_tests
    }
    
    # 检查文档是否存在
    if has_doc and not Path(args.doc).exists():
        print(f"✗ 错误: 文档不存在: {args.doc}")
        return 1
    
    # 确定分支/commit
    branch_or_commit = args.branch or args.commit
    
    # 运行流程
    if has_repo:
        # Git模式
        if not branch_or_commit:
            print("✗ 错误: Git模式需要指定 --branch 或 --commit 参数")
            return 1
        
        results = run_pipeline_with_git(
            repo_url=args.repo,
            branch_or_commit=branch_or_commit,
            doc_path=args.doc,
            output_dir=args.output,
            skip_tests=args.skip_tests,
            generate_excel=not args.no_excel,
            generate_xmind=not args.no_xmind,
            generate_code=not args.no_code,
            keep_repo=args.keep_repo
        )
    else:
        # 本地文档模式
        results = run_pipeline(
            docx_path=args.doc,
            output_dir=args.output,
            skip_tests=args.skip_tests,
            generate_excel=not args.no_excel,
            generate_xmind=not args.no_xmind,
            generate_code=not args.no_code
        )
    
    return 0 if results["success"] else 1


if __name__ == '__main__':
    exit(main())
