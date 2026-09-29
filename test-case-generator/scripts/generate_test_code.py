#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试代码生成模块
支持多语言测试代码生成（Python pytest / Java JUnit）
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


# ============================================================================
# Python pytest 模板
# ============================================================================

PYTEST_FILE_TEMPLATE = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动生成的pytest测试代码
生成时间: {timestamp}
基于需求文档和代码分析自动生成
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List


{test_classes}
'''

PYTEST_CLASS_TEMPLATE = '''
class {class_name}:
    """
    {description}
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置条件"""
{setup_code}
        yield
{teardown_code}
    
{test_methods}
'''

PYTEST_METHOD_TEMPLATE = '''
    def {method_name}(self{params}):
        """{docstring}"""
        # Arrange
{arrange_code}
        
        # Act
{act_code}
        
        # Assert
{assert_code}
'''


# ============================================================================
# Java JUnit 模板
# ============================================================================

JAVA_FILE_TEMPLATE = '''package {package};

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import static org.mockito.ArgumentMatchers.*;

{imports}

/**
 * 自动生成的JUnit测试代码
 * 生成时间: {timestamp}
 */
{test_classes}
'''

JAVA_CLASS_TEMPLATE = '''
@DisplayName("{description}")
class {class_name} {{
    
{setup_methods}
    
{test_methods}
}}
'''

JAVA_SETUP_TEMPLATE = '''
    @BeforeEach
    void setUp() {{
{setup_code}
    }}
    
    @AfterEach
    void tearDown() {{
{teardown_code}
    }}
'''

JAVA_METHOD_TEMPLATE = '''
    @Test
    @DisplayName("{display_name}")
    void {method_name}() {{
        // Arrange
{arrange_code}
        
        // Act
{act_code}
        
        // Assert
{assert_code}
    }}
'''


# ============================================================================
# 代码生成器
# ============================================================================

class TestCodeGenerator:
    """测试代码生成器"""
    
    def __init__(self, language: str = "python", test_framework: str = None):
        """
        初始化生成器
        
        Args:
            language: 编程语言 (python/java/javascript)
            test_framework: 测试框架 (pytest/junit/jest)
        """
        self.language = language.lower()
        self.test_framework = test_framework or self._get_default_framework()
    
    def _get_default_framework(self) -> str:
        """获取默认测试框架"""
        frameworks = {
            "python": "pytest",
            "java": "junit5",
            "javascript": "jest",
            "typescript": "jest"
        }
        return frameworks.get(self.language, "pytest")
    
    def generate(self, test_cases: List[Dict[str, Any]], 
                 output_dir: str,
                 existing_tests: List[str] = None,
                 code_analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """
        生成测试代码
        
        Args:
            test_cases: 测试用例列表
            output_dir: 输出目录
            existing_tests: 已有测试文件列表
            code_analysis: 代码分析结果
            
        Returns:
            生成的文件路径字典
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if self.language == "java":
            return self._generate_java(test_cases, output_path, existing_tests, code_analysis)
        else:
            return self._generate_python(test_cases, output_path, existing_tests, code_analysis)
    
    def _generate_python(self, test_cases: List[Dict[str, Any]],
                         output_path: Path,
                         existing_tests: List[str] = None,
                         code_analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """生成Python pytest测试代码"""
        
        # 按测试类型分组
        grouped = self._group_test_cases(test_cases)
        
        # 生成测试类
        test_classes = []
        for class_name, cases in grouped.items():
            if cases:
                test_class = self._generate_pytest_class(class_name, cases)
                test_classes.append(test_class)
        
        # 生成文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        files = {}
        
        # 主测试文件
        test_code = PYTEST_FILE_TEMPLATE.format(
            timestamp=timestamp,
            test_classes="\n".join(test_classes)
        )
        test_file = output_path / "test_generated.py"
        test_file.write_text(test_code, encoding='utf-8')
        files["test_file"] = str(test_file)
        
        # conftest.py
        conftest_code = self._generate_conftest(code_analysis)
        conftest_file = output_path / "conftest.py"
        conftest_file.write_text(conftest_code, encoding='utf-8')
        files["conftest"] = str(conftest_file)
        
        # requirements.txt
        req_code = self._generate_requirements()
        req_file = output_path / "requirements.txt"
        req_file.write_text(req_code, encoding='utf-8')
        files["requirements"] = str(req_file)
        
        return files
    
    def _generate_pytest_class(self, class_name: str, 
                               test_cases: List[Dict[str, Any]]) -> str:
        """生成pytest测试类"""
        
        # 生成setup代码
        setup_lines = []
        teardown_lines = []
        
        # 生成测试方法
        test_methods = []
        for i, tc in enumerate(test_cases):
            method = self._generate_pytest_method(tc, i)
            test_methods.append(method)
        
        return PYTEST_CLASS_TEMPLATE.format(
            class_name=class_name,
            description=f"{class_name} 测试类，包含 {len(test_cases)} 个测试用例",
            setup_code="\n".join(setup_lines) if setup_lines else "        pass",
            teardown_code="\n".join(teardown_lines) if teardown_lines else "        pass",
            test_methods="\n".join(test_methods)
        )
    
    def _generate_pytest_method(self, tc: Dict[str, Any], index: int) -> str:
        """生成pytest测试方法"""
        
        # 方法名
        method_name = f"test_{tc['id'].lower()}_{index}"
        
        # 文档字符串
        docstring = tc.get('description', tc.get('name', ''))
        docstring = docstring.replace('\n', '\n        ')
        
        # 生成Arrange代码
        arrange_lines = self._generate_pytestArrange(tc)
        
        # 生成Act代码
        act_lines = self._generate_pytest_act(tc)
        
        # 生成Assert代码
        assert_lines = self._generate_pytest_assert(tc)
        
        return PYTEST_METHOD_TEMPLATE.format(
            method_name=method_name,
            params="",
            docstring=docstring,
            arrange_code="\n".join(arrange_lines),
            act_code="\n".join(act_lines),
            assert_code="\n".join(assert_lines)
        )
    
    def _generate_pytestArrange(self, tc: Dict[str, Any]) -> List[str]:
        """生成pytest的Arrange代码"""
        lines = []
        test_type = tc.get('test_type', '功能测试')
        preconditions = tc.get('preconditions', [])
        steps = tc.get('steps', [])
        name = tc.get('name', '').lower()
        description = tc.get('description', '').lower()
        
        # 分析测试场景并生成具体代码
        if 'mock' in description or '模拟' in description or '模拟' in name:
            lines.append("        # 使用Mock模拟外部依赖")
            lines.append("        mock_service = Mock()")
            lines.append("        mock_service.get.return_value = None")
        
        if '数据库' in description or 'database' in description or '数据库' in name:
            lines.append("        # Mock数据库操作")
            lines.append("        mock_db = Mock()")
            lines.append("        mock_db.query.return_value = []")
        
        if 'api' in description.lower() or '接口' in description or 'api' in name:
            lines.append("        # Mock API调用")
            lines.append("        mock_api = Mock()")
            lines.append("        mock_api.request.return_value = {'status': 'ok'}")
        
        # 根据测试数据生成
        if tc.get('test_data'):
            lines.append(f"        test_data = {json.dumps(tc['test_data'], ensure_ascii=False)}")
        
        # 根据前置条件生成
        for pre in preconditions[:2]:
            if '登录' in pre or 'login' in pre.lower():
                lines.append("        # 模拟用户已登录状态")
                lines.append("        session = {'user_id': 1, 'logged_in': True}")
            elif '权限' in pre or 'permission' in pre.lower():
                lines.append("        # 设置权限")
                lines.append("        permissions = ['read', 'write']")
        
        if not lines:
            lines.append("        # 准备测试数据")
        
        return lines
    
    def _generate_pytest_act(self, tc: Dict[str, Any]) -> List[str]:
        """生成pytest的Act代码"""
        lines = []
        steps = tc.get('steps', [])
        description = tc.get('description', '')
        name = tc.get('name', '')
        
        # 分析步骤生成代码
        for i, step in enumerate(steps[:3]):
            step_lower = step.lower()
            
            if '调用' in step or 'call' in step_lower:
                # 提取方法名
                if '.' in step:
                    # 格式: "调用xxx.xxx方法"
                    method_part = step.split('调用')[-1].split('：')[0].split(':')[0].strip()
                    parts = method_part.replace('方法', '').split('.')
                    if len(parts) >= 2:
                        class_name = parts[0]
                        method_name = parts[1]
                        lines.append(f"        # 调用 {class_name}.{method_name}")
                        lines.append(f"        result = {class_name.lower()}.{method_name}()")
                    else:
                        method_name = parts[0]
                        lines.append(f"        # 调用 {method_name}")
                        lines.append(f"        result = service.{method_name}()")
                else:
                    lines.append("        # 执行操作")
                    lines.append("        result = service.execute()")
            
            elif '请求' in step or 'request' in step_lower:
                lines.append("        # 发送请求")
                lines.append("        response = client.get('/api/endpoint')")
            
            elif '输入' in step or 'input' in step_lower:
                lines.append("        # 处理输入")
                lines.append("        result = process_input(test_data)")
            
            elif '验证' in step or '检查' in step or 'verify' in step_lower:
                lines.append(f"        # {step}")
                # 在act阶段不验证，放到assert阶段
            
            else:
                lines.append(f"        # {step}")
                if i == 0:
                    lines.append("        result = service.method_under_test()")
        
        if not lines:
            lines.append("        # 执行被测试的方法")
            lines.append("        result = service.method_under_test()")
        
        return lines
    
    def _generate_pytest_assert(self, tc: Dict[str, Any]) -> List[str]:
        """生成pytest的Assert代码"""
        lines = []
        test_type = tc.get('test_type', '功能测试')
        expected_results = tc.get('expected_results', [])
        description = tc.get('description', '')
        name = tc.get('name', '')
        
        # 根据测试类型生成断言
        if test_type == '异常测试':
            lines.append("        # 验证抛出异常")
            lines.append("        with pytest.raises(Exception) as exc_info:")
            lines.append("            service.method_under_test()")
            lines.append(f'        assert "错误" in str(exc_info.value) or "error" in str(exc_info.value).lower()')
        
        elif test_type == '边界测试':
            lines.append("        # 验证边界条件处理")
            lines.append("        assert result is not None")
            lines.append("        assert result != ''")
        
        else:  # 功能测试
            if expected_results:
                for er in expected_results[:2]:
                    er_lower = er.lower()
                    
                    if '成功' in er or 'success' in er_lower:
                        lines.append("        # 验证操作成功")
                        lines.append("        assert result is not None")
                        lines.append("        assert result.get('success') == True or result.get('status') == 'ok'")
                    
                    elif '返回' in er or 'return' in er_lower:
                        lines.append("        # 验证返回结果")
                        lines.append("        assert result is not None")
                        lines.append("        assert isinstance(result, (dict, list, str))")
                    
                    elif '跳转' in er or 'redirect' in er_lower:
                        lines.append("        # 验证跳转")
                        lines.append("        assert response.status_code in [200, 301, 302]")
                    
                    elif '显示' in er or 'display' in er_lower:
                        lines.append("        # 验证显示内容")
                        lines.append("        assert 'expected_content' in str(result)")
                    
                    elif '锁定' in er or 'lock' in er_lower:
                        lines.append("        # 验证账户锁定")
                        lines.append("        assert result.get('locked') == True or result.get('status') == 'locked'")
                    
                    else:
                        lines.append(f"        # 验证: {er}")
                        lines.append("        assert result is not None")
            
            if not lines:
                lines.append("        # 验证结果")
                lines.append("        assert result is not None")
        
        return lines
    
    def _generate_conftest(self, code_analysis: Dict[str, Any] = None) -> str:
        """生成conftest.py"""
        return '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pytest配置和fixtures"""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture(scope="session")
def test_config():
    """测试配置"""
    return {
        "base_url": "http://localhost:8000",
        "timeout": 30
    }


@pytest.fixture
def mock_service():
    """Mock服务对象"""
    return Mock()


@pytest.fixture
def mock_db():
    """Mock数据库"""
    mock = Mock()
    mock.query.return_value = []
    mock.insert.return_value = True
    mock.update.return_value = True
    mock.delete.return_value = True
    return mock
'''
    
    def _generate_requirements(self) -> str:
        """生成requirements.txt"""
        return '''# 测试依赖
pytest>=7.0.0
pytest-html>=3.2.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-asyncio>=0.21.0

# Mock工具
faker>=18.0.0

# API测试
requests>=2.28.0
'''
    
    def _generate_java(self, test_cases: List[Dict[str, Any]],
                       output_path: Path,
                       existing_tests: List[str] = None,
                       code_analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """生成Java JUnit测试代码"""
        
        # 按测试类型分组
        grouped = self._group_test_cases(test_cases)
        
        # 生成测试类
        test_classes = []
        all_imports = set()
        
        for class_name, cases in grouped.items():
            if cases:
                test_class, imports = self._generate_java_class(class_name, cases)
                test_classes.append(test_class)
                all_imports.update(imports)
        
        # 生成文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        files = {}
        
        # 主测试文件
        imports_str = "\n".join([f"import {imp};" for imp in all_imports])
        test_code = JAVA_FILE_TEMPLATE.format(
            package="com.example.test",
            imports=imports_str,
            timestamp=timestamp,
            test_classes="\n".join(test_classes)
        )
        test_file = output_path / "GeneratedTest.java"
        test_file.write_text(test_code, encoding='utf-8')
        files["test_file"] = str(test_file)
        
        return files
    
    def _generate_java_class(self, class_name: str,
                             test_cases: List[Dict[str, Any]]) -> tuple:
        """生成Java测试类"""
        imports = set()
        
        # 生成setUp和tearDown
        setup_methods = []
        test_methods = []
        
        for i, tc in enumerate(test_cases):
            method, method_imports = self._generate_java_method(tc, i)
            test_methods.append(method)
            imports.update(method_imports)
        
        setup_code = JAVA_SETUP_TEMPLATE.format(
            setup_code="        // 初始化测试环境",
            teardown_code="        // 清理测试环境"
        )
        
        test_class = JAVA_CLASS_TEMPLATE.format(
            description=f"{class_name} 测试类",
            class_name=class_name,
            setup_methods=setup_code,
            test_methods="\n".join(test_methods)
        )
        
        return test_class, imports
    
    def _generate_java_method(self, tc: Dict[str, Any], index: int) -> tuple:
        """生成Java测试方法"""
        imports = set()
        
        # 方法名
        method_name = f"test{tc['id']}_{index}"
        
        # 显示名称
        display_name = tc.get('name', f'Test case {tc["id"]}')
        
        # 生成Arrange代码
        arrange_lines = self._generate_javaArrange(tc, imports)
        
        # 生成Act代码
        act_lines = self._generate_java_act(tc, imports)
        
        # 生成Assert代码
        assert_lines = self._generate_java_assert(tc, imports)
        
        method = JAVA_METHOD_TEMPLATE.format(
            display_name=display_name,
            method_name=method_name,
            arrange_code="\n".join(arrange_lines),
            act_code="\n".join(act_lines),
            assert_code="\n".join(assert_lines)
        )
        
        return method, imports
    
    def _generate_javaArrange(self, tc: Dict[str, Any], imports: set) -> List[str]:
        """生成Java的Arrange代码"""
        lines = []
        description = tc.get('description', '').lower()
        
        if 'mock' in description or '模拟' in description:
            imports.add("org.mockito.Mock")
            imports.add("org.mockito.MockitoAnnotations")
            lines.append("        // 使用Mock模拟外部依赖")
            lines.append("        MockService mockService = mock(MockService.class);")
            lines.append("        when(mockService.getData()).thenReturn(null);")
        
        if '数据库' in description or 'database' in description:
            imports.add("org.mockito.Mock")
            lines.append("        // Mock数据库")
            lines.append("        MockRepository mockRepo = mock(MockRepository.class);")
        
        if not lines:
            lines.append("        // 准备测试数据")
        
        return lines
    
    def _generate_java_act(self, tc: Dict[str, Any], imports: set) -> List[str]:
        """生成Java的Act代码"""
        lines = []
        steps = tc.get('steps', [])
        
        if steps:
            lines.append(f"        // {steps[0]}")
        
        lines.append("        Object result = service.methodUnderTest();")
        
        return lines
    
    def _generate_java_assert(self, tc: Dict[str, Any], imports: set) -> List[str]:
        """生成Java的Assert代码"""
        imports.add("static org.junit.jupiter.api.Assertions.*")
        lines = []
        test_type = tc.get('test_type', '功能测试')
        
        if test_type == '异常测试':
            imports.add("org.junit.jupiter.api.Assertions.assertThrows")
            lines.append("        // 验证抛出异常")
            lines.append("        assertThrows(Exception.class, () -> {")
            lines.append("            service.methodUnderTest();")
            lines.append("        });")
        else:
            lines.append("        // 验证结果")
            lines.append("        assertNotNull(result);")
        
        return lines
    
    def _group_test_cases(self, test_cases: List[Dict[str, Any]]) -> Dict[str, List]:
        """按测试类型分组"""
        grouped = {}
        for tc in test_cases:
            test_type = tc.get('test_type', '功能测试')
            class_name = self._get_class_name(test_type)
            if class_name not in grouped:
                grouped[class_name] = []
            grouped[class_name].append(tc)
        return grouped
    
    def _get_class_name(self, test_type: str) -> str:
        """根据测试类型获取类名"""
        class_names = {
            '功能测试': 'TestFunctional',
            '边界测试': 'TestBoundary',
            '异常测试': 'TestException',
            '性能测试': 'TestPerformance',
            '安全测试': 'TestSecurity'
        }
        return class_names.get(test_type, 'TestGeneral')


def generate_test_code(test_cases: List[Dict[str, Any]], 
                      output_dir: str,
                      language: str = "python",
                      test_framework: str = None,
                      existing_tests: List[str] = None,
                      code_analysis: Dict[str, Any] = None) -> Dict[str, str]:
    """
    生成测试代码的便捷函数
    
    Args:
        test_cases: 测试用例列表
        output_dir: 输出目录
        language: 编程语言
        test_framework: 测试框架
        existing_tests: 已有测试文件
        code_analysis: 代码分析结果
        
    Returns:
        生成的文件路径字典
    """
    generator = TestCodeGenerator(language, test_framework)
    return generator.generate(test_cases, output_dir, existing_tests, code_analysis)


def main():
    parser = argparse.ArgumentParser(description='生成测试代码')
    parser.add_argument('input', help='输入测试用例JSON文件路径')
    parser.add_argument('--output', '-o', default='./generated_tests', 
                       help='输出目录（默认: ./generated_tests）')
    parser.add_argument('--language', '-l', default='python',
                       choices=['python', 'java', 'javascript'],
                       help='目标语言（默认: python）')
    parser.add_argument('--framework', '-f', help='测试框架（自动检测）')
    
    args = parser.parse_args()
    
    try:
        # 读取测试用例
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取测试用例列表
        if isinstance(data, dict) and 'test_cases' in data:
            test_cases = data['test_cases']
        elif isinstance(data, list):
            test_cases = data
        else:
            test_cases = [data]
        
        # 生成测试代码
        files = generate_test_code(
            test_cases, 
            args.output,
            language=args.language,
            test_framework=args.framework
        )
        
        print(f"\n✓ 共生成 {len(test_cases)} 个测试用例的测试代码")
        print(f"\n生成的文件:")
        for name, path in files.items():
            print(f"  - {name}: {path}")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
