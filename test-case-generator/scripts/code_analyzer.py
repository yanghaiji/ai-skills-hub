#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
代码结构分析模块
分析项目结构、检测测试框架、识别代码风格
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict


class CodeAnalyzer:
    """代码分析器"""
    
    # 常见的测试框架配置文件
    TEST_CONFIG_FILES = {
        'pytest': ['pytest.ini', 'setup.cfg', 'pyproject.toml', 'conftest.py'],
        'unittest': ['unittest.cfg'],
        'jest': ['jest.config.js', 'jest.config.ts', 'jest.config.json'],
        'mocha': ['.mocharc.yml', '.mocharc.json', '.mocharc.js'],
        'vitest': ['vitest.config.ts', 'vitest.config.js'],
    }
    
    # 常见的依赖文件
    DEPENDENCY_FILES = {
        'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
        'javascript': ['package.json', 'yarn.lock', 'package-lock.json'],
        'java': ['pom.xml', 'build.gradle'],
        'go': ['go.mod'],
        'rust': ['Cargo.toml'],
    }
    
    # 测试目录模式
    TEST_DIR_PATTERNS = ['test', 'tests', '__tests__', 'spec', 'specs']
    
    def __init__(self, repo_dir: str):
        self.repo_dir = Path(repo_dir)
        self.analysis_result = {
            "language": "",
            "framework": "",
            "test_framework": "",
            "project_structure": {},
            "existing_tests": [],
            "code_style": {},
            "dependencies": [],
            "test_patterns": []
        }
    
    def analyze(self) -> Dict[str, Any]:
        """
        执行完整的代码分析
        
        Returns:
            分析结果字典
        """
        print("  正在分析项目结构...")
        self._analyze_project_structure()
        
        print("  正在检测编程语言...")
        self._detect_language()
        
        print("  正在检测测试框架...")
        self._detect_test_framework()
        
        print("  正在查找已有测试...")
        self._find_existing_tests()
        
        print("  正在分析代码风格...")
        self._analyze_code_style()
        
        print("  正在解析依赖...")
        self._parse_dependencies()
        
        return self.analysis_result
    
    def _analyze_project_structure(self):
        """分析项目结构"""
        structure = {
            "root_files": [],
            "directories": [],
            "src_dirs": [],
            "test_dirs": []
        }
        
        try:
            for item in self.repo_dir.iterdir():
                if item.name.startswith('.'):
                    continue
                    
                if item.is_file():
                    structure["root_files"].append(item.name)
                elif item.is_dir():
                    structure["directories"].append(item.name)
                    
                    # 识别源代码目录
                    if item.name in ['src', 'lib', 'app', 'source']:
                        structure["src_dirs"].append(item.name)
                    
                    # 识别测试目录
                    if item.name.lower() in self.TEST_DIR_PATTERNS:
                        structure["test_dirs"].append(item.name)
        
        except Exception as e:
            print(f"  ⚠ 分析项目结构时出错: {e}")
        
        self.analysis_result["project_structure"] = structure
    
    def _detect_language(self):
        """检测主要编程语言"""
        language_indicators = {
            'python': ['.py', 'requirements.txt', 'setup.py', 'pyproject.toml'],
            'javascript': ['.js', '.jsx', 'package.json'],
            'typescript': ['.ts', '.tsx', 'tsconfig.json'],
            'java': ['.java', 'pom.xml', 'build.gradle'],
            'go': ['.go', 'go.mod'],
            'rust': ['.rs', 'Cargo.toml'],
            'csharp': ['.cs', '.csproj'],
            'cpp': ['.cpp', '.cc', '.h', '.hpp'],
        }
        
        file_count = defaultdict(int)
        
        # 统计文件扩展名
        try:
            for root, dirs, files in os.walk(self.repo_dir):
                # 排除隐藏目录和node_modules等
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'vendor', '__pycache__']]
                
                for file in files:
                    ext = Path(file).suffix.lower()
                    for lang, indicators in language_indicators.items():
                        if ext in indicators:
                            file_count[lang] += 1
        except Exception:
            pass
        
        if file_count:
            self.analysis_result["language"] = max(file_count, key=file_count.get)
        else:
            self.analysis_result["language"] = "unknown"
    
    def _detect_test_framework(self):
        """检测测试框架"""
        detected_frameworks = []
        
        # 检查配置文件
        for framework, config_files in self.TEST_CONFIG_FILES.items():
            for config_file in config_files:
                if (self.repo_dir / config_file).exists():
                    detected_frameworks.append(framework)
        
        # 检查package.json中的依赖（JavaScript）
        package_json = self.repo_dir / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    pkg = json.load(f)
                    deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                    
                    js_test_frameworks = ['jest', 'mocha', 'vitest', 'jasmine', 'ava']
                    for framework in js_test_frameworks:
                        if framework in deps:
                            detected_frameworks.append(framework)
            except Exception:
                pass
        
        # 检查requirements.txt中的依赖（Python）
        requirements = self.repo_dir / 'requirements.txt'
        if requirements.exists():
            try:
                with open(requirements, 'r') as f:
                    content = f.read().lower()
                    if 'pytest' in content:
                        detected_frameworks.append('pytest')
                    if 'unittest' in content:
                        detected_frameworks.append('unittest')
            except Exception:
                pass
        
        # 优先级排序
        priority_order = ['pytest', 'jest', 'mocha', 'vitest', 'unittest']
        for framework in priority_order:
            if framework in detected_frameworks:
                self.analysis_result["test_framework"] = framework
                return
        
        if detected_frameworks:
            self.analysis_result["test_framework"] = detected_frameworks[0]
        else:
            self.analysis_result["test_framework"] = "unknown"
    
    def _find_existing_tests(self):
        """查找已有的测试文件"""
        test_files = []
        
        # 测试文件模式
        test_patterns = [
            r'test_.*\.py$',
            r'_test\.py$',
            r'.*\.test\.js$',
            r'.*\.test\.ts$',
            r'.*\.spec\.js$',
            r'.*\.spec\.ts$',
            r'Test.*\.java$',
            r'.*Test\.java$',
        ]
        
        try:
            for root, dirs, files in os.walk(self.repo_dir):
                # 排除隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'vendor']]
                
                for file in files:
                    for pattern in test_patterns:
                        if re.match(pattern, file, re.IGNORECASE):
                            rel_path = os.path.relpath(os.path.join(root, file), self.repo_dir)
                            test_files.append(rel_path)
                            break
        except Exception:
            pass
        
        self.analysis_result["existing_tests"] = test_files[:50]  # 限制数量
    
    def _analyze_code_style(self):
        """分析代码风格"""
        style_info = {
            "indentation": "unknown",
            "quote_style": "unknown",
            "naming_convention": "unknown"
        }
        
        # 分析Python代码风格
        if self.analysis_result["language"] == "python":
            py_files = list(self.repo_dir.rglob("*.py"))[:5]  # 取前5个文件分析
            
            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # 检测缩进
                    if '    ' in content:
                        style_info["indentation"] = "4 spaces"
                    elif '\t' in content:
                        style_info["indentation"] = "tabs"
                    
                    # 检测引号风格
                    single_quotes = content.count("'")
                    double_quotes = content.count('"')
                    style_info["quote_style"] = "single" if single_quotes > double_quotes else "double"
                    
                    break
                except Exception:
                    continue
        
        self.analysis_result["code_style"] = style_info
    
    def _parse_dependencies(self):
        """解析项目依赖"""
        dependencies = []
        
        # Python依赖
        requirements = self.repo_dir / 'requirements.txt'
        if requirements.exists():
            try:
                with open(requirements, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dependencies.append({
                                "name": line.split('==')[0].split('>=')[0].split('<=')[0],
                                "version": line,
                                "type": "python"
                            })
            except Exception:
                pass
        
        # JavaScript依赖
        package_json = self.repo_dir / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    pkg = json.load(f)
                    deps = pkg.get('dependencies', {})
                    dev_deps = pkg.get('devDependencies', {})
                    
                    for name, version in deps.items():
                        dependencies.append({
                            "name": name,
                            "version": version,
                            "type": "javascript",
                            "dev": False
                        })
                    
                    for name, version in dev_deps.items():
                        dependencies.append({
                            "name": name,
                            "version": version,
                            "type": "javascript",
                            "dev": True
                        })
            except Exception:
                pass
        
        self.analysis_result["dependencies"] = dependencies
    
    def get_test_style_example(self) -> Optional[str]:
        """
        获取已有测试的代码示例
        
        Returns:
            测试代码示例字符串
        """
        if not self.analysis_result["existing_tests"]:
            return None
        
        # 读取第一个测试文件
        first_test = self.repo_dir / self.analysis_result["existing_tests"][0]
        try:
            with open(first_test, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # 限制长度
                if len(content) > 2000:
                    content = content[:2000] + "\n... (truncated)"
                return content
        except Exception:
            return None
    
    def get_summary(self) -> str:
        """
        获取分析结果摘要
        
        Returns:
            格式化的摘要字符串
        """
        lines = [
            "=" * 60,
            "  代码分析结果摘要",
            "=" * 60,
            f"  编程语言: {self.analysis_result['language']}",
            f"  测试框架: {self.analysis_result['test_framework']}",
            f"  已有测试文件数: {len(self.analysis_result['existing_tests'])}",
        ]
        
        structure = self.analysis_result["project_structure"]
        if structure.get("test_dirs"):
            lines.append(f"  测试目录: {', '.join(structure['test_dirs'])}")
        
        if structure.get("src_dirs"):
            lines.append(f"  源代码目录: {', '.join(structure['src_dirs'])}")
        
        if self.analysis_result["code_style"].get("indentation") != "unknown":
            lines.append(f"  缩进风格: {self.analysis_result['code_style']['indentation']}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def analyze_project(repo_dir: str) -> Dict[str, Any]:
    """
    分析项目结构的便捷函数
    
    Args:
        repo_dir: 仓库目录
        
    Returns:
        分析结果
    """
    analyzer = CodeAnalyzer(repo_dir)
    return analyzer.analyze()


def main():
    parser = argparse.ArgumentParser(description='代码结构分析')
    parser.add_argument('repo_dir', help='仓库目录路径')
    parser.add_argument('--summary', action='store_true', help='显示摘要')
    parser.add_argument('--output', '-o', help='输出JSON文件路径')
    
    args = parser.parse_args()
    
    analyzer = CodeAnalyzer(args.repo_dir)
    result = analyzer.analyze()
    
    if args.summary:
        print(analyzer.get_summary())
    elif args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✓ 分析结果已保存到: {args.output}")
    else:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
