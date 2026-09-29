#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一测试代码生成器
无论项目是什么语言，都用Python pytest生成测试代码
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


# ============================================================================
# Python pytest 统一测试模板（适用于任何项目）
# ============================================================================

UNIFIED_TEST_TEMPLATE = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动生成的统一测试代码
生成时间: {timestamp}
项目类型: {project_type}
使用Python pytest测试任何后端服务
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List, Optional
import json
import time


# ============================================================================
# 配置
# ============================================================================

BASE_URL = "{base_url}"
API_PREFIX = "{api_prefix}"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def base_url():
    """API基础地址"""
    return BASE_URL


@pytest.fixture(scope="session")
def api_client(base_url):
    """API客户端"""
    session = requests.Session()
    session.base_url = base_url
    session.headers.update({{
        "Content-Type": "application/json",
        "Accept": "application/json"
    }})
    return session


@pytest.fixture
def auth_token(api_client):
    """获取认证Token"""
    # TODO: 根据实际项目实现登录逻辑
    response = api_client.post(f"{{api_client.base_url}}/auth/login", json={{
        "username": "test_user",
        "password": "test_password"
    }})
    if response.status_code == 200:
        return response.json().get("token")
    return "mock_token"


@pytest.fixture
def mock_response():
    """Mock响应对象"""
    def _create_response(status_code=200, json_data=None, text=""):
        mock = Mock()
        mock.status_code = status_code
        mock.json.return_value = json_data or {{}}
        mock.text = text
        mock.ok = 200 <= status_code < 300
        return mock
    return _create_response


# ============================================================================
# 工具函数
# ============================================================================

def assert_response_success(response, expected_status=200):
    """断言响应成功"""
    assert response.status_code == expected_status, \\
        f"期望状态码 {{expected_status}}，实际 {{response.status_code}}"
    return response.json()


def assert_response_error(response, expected_status=400):
    """断言响应错误"""
    assert response.status_code == expected_status, \\
        f"期望状态码 {{expected_status}}，实际 {{response.status_code}}"


def assert_json_contains(data, *keys):
    """断言JSON包含指定字段"""
    for key in keys:
        assert key in data, f"JSON中缺少字段: {{key}}"


# ============================================================================
# 测试类
# ============================================================================

{test_classes}
'''

# 功能测试类模板
FUNCTIONAL_TEST_CLASS = '''
class Test{class_name}:
    """
    {description}
    测试用例数量: {test_count}
    """
    
{test_methods}
'''

# 功能测试方法模板
FUNCTIONAL_TEST_METHOD = '''
    def test_{method_name}(self, api_client{extra_params}):
        """{docstring}"""
        # Arrange
{arrange_code}
        
        # Act
{act_code}
        
        # Assert
{assert_code}
'''

# API测试方法模板
API_TEST_METHOD = '''
    def test_{method_name}(self, api_client{extra_params}):
        """{docstring}"""
        # Arrange
        url = f"{{BASE_URL}}{endpoint}"
        payload = {payload}
        
        # Act
        response = api_client.{http_method}(url, json=payload)
        
        # Assert
        assert response.status_code == {expected_status}
        data = response.json()
        assert_json_contains(data, {assert_fields})
'''

# Mock测试方法模板
MOCK_TEST_METHOD = '''
    def test_{method_name}_with_mock(self{extra_params}):
        """{docstring}（使用Mock）"""
        # Arrange
        with patch('{mock_target}') as mock_obj:
            mock_obj.{mock_method}.return_value = {mock_return}
            
            # Act
{act_code}
            
            # Assert
{assert_code}
'''

# requirements.txt
REQUIREMENTS_TEMPLATE = '''# 测试依赖
pytest>=7.0.0
pytest-html>=3.2.0
pytest-cov>=4.0.0
requests>=2.28.0

# Mock工具
pytest-mock>=3.10.0
responses>=0.23.0

# 数据处理
faker>=18.0.0
jsonschema>=4.17.0
'''

# README
README_TEMPLATE = '''# 自动生成的统一测试代码

## 概述

本测试代码适用于任何类型的后端项目，使用Python pytest作为测试框架。

- 生成时间: {timestamp}
- 项目类型: {project_type}
- 测试用例数: {test_count}

## 使用方式

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境
修改 `test_generated.py` 中的配置：
```python
BASE_URL = "http://localhost:8080"  # 你的服务地址
API_PREFIX = "/api"  # API前缀
```

### 3. 运行测试
```bash
# 运行所有测试
pytest -v

# 运行特定测试
pytest -v -k "test_login"

# 生成HTML报告
pytest --html=report.html
```

## 测试类型

### 功能测试
验证API功能是否正常工作

### 边界测试
验证边界条件处理

### 异常测试
验证异常处理能力

## 注意事项

1. 根据实际项目修改 `BASE_URL` 和 `API_PREFIX`
2. 根据实际API修改请求参数和断言
3. 外部依赖使用Mock模拟
'''


class UnifiedTestGenerator:
    """统一测试代码生成器"""
    
    def __init__(self, 
                 project_type: str = "unknown",
                 base_url: str = "http://localhost:8080",
                 api_prefix: str = "/api"):
        """
        初始化生成器
        
        Args:
            project_type: 项目类型 (java-spring/python-flask/node-express等)
            base_url: 服务基础地址
            api_prefix: API前缀
        """
        self.project_type = project_type
        self.base_url = base_url
        self.api_prefix = api_prefix
    
    def generate(self, test_cases: List[Dict[str, Any]], 
                 output_dir: str,
                 api_endpoints: List[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        生成测试代码
        
        Args:
            test_cases: 测试用例列表
            output_dir: 输出目录
            api_endpoints: API端点列表（可选）
            
        Returns:
            生成的文件路径字典
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成测试类
        test_classes = []
        
        # 按测试类型分组
        grouped = self._group_test_cases(test_cases)
        
        for class_name, cases in grouped.items():
            if cases:
                test_class = self._generate_test_class(class_name, cases)
                test_classes.append(test_class)
        
        # 如果有API端点，添加API测试
        if api_endpoints:
            api_test_class = self._generate_api_test_class(api_endpoints)
            test_classes.append(api_test_class)
        
        # 生成文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        files = {}
        
        # 主测试文件
        test_code = UNIFIED_TEST_TEMPLATE.format(
            timestamp=timestamp,
            project_type=self.project_type,
            base_url=self.base_url,
            api_prefix=self.api_prefix,
            test_classes="\n".join(test_classes)
        )
        test_file = output_path / "test_generated.py"
        test_file.write_text(test_code, encoding='utf-8')
        files["test_file"] = str(test_file)
        
        # requirements.txt
        req_file = output_path / "requirements.txt"
        req_file.write_text(REQUIREMENTS_TEMPLATE, encoding='utf-8')
        files["requirements"] = str(req_file)
        
        # README.md
        readme_content = README_TEMPLATE.format(
            timestamp=timestamp,
            project_type=self.project_type,
            test_count=len(test_cases)
        )
        readme_file = output_path / "README.md"
        readme_file.write_text(readme_content, encoding='utf-8')
        files["readme"] = str(readme_file)
        
        return files
    
    def _generate_test_class(self, class_name: str, 
                             test_cases: List[Dict[str, Any]]) -> str:
        """生成测试类"""
        test_methods = []
        
        for i, tc in enumerate(test_cases):
            method = self._generate_test_method(tc, i)
            test_methods.append(method)
        
        return FUNCTIONAL_TEST_CLASS.format(
            class_name=class_name,
            description=f"{class_name} 测试类，包含 {len(test_cases)} 个测试用例",
            test_count=len(test_cases),
            test_methods="\n".join(test_methods)
        )
    
    def _generate_test_method(self, tc: Dict[str, Any], index: int) -> str:
        """生成测试方法"""
        
        # 方法名
        method_name = f"{tc['id'].lower()}_{index}"
        
        # 文档字符串
        docstring = tc.get('description', tc.get('name', ''))
        
        # 测试类型
        test_type = tc.get('test_type', '功能测试')
        steps = tc.get('steps', [])
        expected_results = tc.get('expected_results', [])
        preconditions = tc.get('preconditions', [])
        
        # 分析步骤和预期结果，生成具体代码
        arrange_lines = self._generateArrange(tc)
        act_lines = self._generate_act(tc)
        assert_lines = self._generate_assert(tc)
        
        # 判断是否需要额外参数
        extra_params = ""
        if '登录' in str(preconditions) or '认证' in str(preconditions):
            extra_params = ", auth_token"
        
        return FUNCTIONAL_TEST_METHOD.format(
            method_name=method_name,
            extra_params=extra_params,
            docstring=docstring,
            arrange_code="\n".join(arrange_lines),
            act_code="\n".join(act_lines),
            assert_code="\n".join(assert_lines)
        )
    
    def _generateArrange(self, tc: Dict[str, Any]) -> List[str]:
        """生成Arrange代码"""
        lines = []
        test_type = tc.get('test_type', '功能测试')
        steps = tc.get('steps', [])
        name = tc.get('name', '')
        
        # 根据测试类型生成不同的准备代码
        if test_type == '异常测试':
            lines.append("        # 准备异常测试数据")
            lines.append("        invalid_data = {\"invalid\": \"data\"}")
        
        elif test_type == '边界测试':
            lines.append("        # 准备边界测试数据")
            lines.append("        boundary_data = {\"edge_case\": True}")
        
        else:
            # 功能测试
            if '登录' in name or 'login' in name.lower():
                lines.append("        # 准备登录数据")
                lines.append("        login_data = {")
                lines.append("            \"username\": \"test_user\",")
                lines.append("            \"password\": \"test_password\"")
                lines.append("        }")
            
            elif '查询' in name or 'query' in name.lower() or 'get' in name.lower():
                lines.append("        # 准备查询参数")
                lines.append("        params = {\"page\": 1, \"size\": 10}")
            
            elif '创建' in name or 'create' in name.lower() or 'add' in name.lower():
                lines.append("        # 准备创建数据")
                lines.append("        create_data = {")
                lines.append("            \"name\": \"test_name\",")
                lines.append("            \"description\": \"test_description\"")
                lines.append("        }")
            
            elif '更新' in name or 'update' in name.lower() or 'modify' in name.lower():
                lines.append("        # 准备更新数据")
                lines.append("        update_data = {")
                lines.append("            \"id\": 1,")
                lines.append("            \"name\": \"updated_name\"")
                lines.append("        }")
            
            elif '删除' in name or 'delete' in name.lower() or 'remove' in name.lower():
                lines.append("        # 准备删除目标")
                lines.append("        target_id = 1")
            
            else:
                lines.append("        # 准备测试数据")
                lines.append("        test_data = {}")
        
        return lines
    
    def _generate_act(self, tc: Dict[str, Any]) -> List[str]:
        """生成Act代码"""
        lines = []
        steps = tc.get('steps', [])
        name = tc.get('name', '')
        test_type = tc.get('test_type', '功能测试')
        
        # 根据步骤和名称生成调用代码
        for i, step in enumerate(steps[:2]):  # 只处理前2步
            step_lower = step.lower()
            
            if '调用' in step or 'call' in step_lower or '请求' in step:
                # 提取API端点
                if '/' in step:
                    # 找到API路径
                    import re
                    endpoint_match = re.search(r'/[\w/]+', step)
                    if endpoint_match:
                        endpoint = endpoint_match.group(0)
                        lines.append(f"        # 调用API: {endpoint}")
                        lines.append(f"        response = api_client.get(f\"{{BASE_URL}}{endpoint}\")")
                    else:
                        lines.append("        # 发送请求")
                        lines.append("        response = api_client.get(f\"{{BASE_URL}}/api/endpoint\")")
                else:
                    lines.append("        # 发送请求")
                    lines.append("        response = api_client.get(f\"{{BASE_URL}}/api/endpoint\")")
            
            elif '登录' in step or 'login' in step_lower:
                lines.append("        # 执行登录")
                lines.append("        response = api_client.post(f\"{{BASE_URL}}/auth/login\", json=login_data)")
            
            elif '查询' in step or 'query' in step_lower or 'get' in step_lower:
                lines.append("        # 执行查询")
                lines.append("        response = api_client.get(f\"{{BASE_URL}}/api/query\", params=params)")
            
            elif '创建' in step or 'create' in step_lower:
                lines.append("        # 执行创建")
                lines.append("        response = api_client.post(f\"{{BASE_URL}}/api/create\", json=create_data)")
            
            elif '更新' in step or 'update' in step_lower:
                lines.append("        # 执行更新")
                lines.append("        response = api_client.put(f\"{{BASE_URL}}/api/update\", json=update_data)")
            
            elif '删除' in step or 'delete' in step_lower:
                lines.append("        # 执行删除")
                lines.append("        response = api_client.delete(f\"{{BASE_URL}}/api/delete/{{target_id}}\")")
            
            else:
                lines.append(f"        # {step}")
                if i == 0:
                    lines.append("        response = api_client.get(f\"{{BASE_URL}}/api/endpoint\")")
        
        if not lines:
            lines.append("        # 发送请求")
            lines.append("        response = api_client.get(f\"{{BASE_URL}}/api/endpoint\")")
        
        return lines
    
    def _generate_assert(self, tc: Dict[str, Any]) -> List[str]:
        """生成Assert代码"""
        lines = []
        test_type = tc.get('test_type', '功能测试')
        expected_results = tc.get('expected_results', [])
        name = tc.get('name', '')
        
        # 根据测试类型生成断言
        if test_type == '异常测试':
            lines.append("        # 验证异常响应")
            lines.append("        assert_response_error(response, 400)")
            lines.append("        data = response.json()")
            lines.append("        assert \"error\" in data or \"message\" in data")
        
        elif test_type == '边界测试':
            lines.append("        # 验证边界条件处理")
            lines.append("        assert response.status_code in [200, 400, 422]")
            lines.append("        data = response.json()")
            lines.append("        assert \"data\" in data or \"error\" in data")
        
        else:
            # 功能测试
            if expected_results:
                for er in expected_results[:2]:
                    er_lower = er.lower()
                    
                    if '成功' in er or 'success' in er_lower:
                        lines.append("        # 验证操作成功")
                        lines.append("        assert_response_success(response)")
                        lines.append("        data = response.json()")
                        lines.append("        assert data.get(\"success\") == True or data.get(\"code\") == 200")
                    
                    elif '返回' in er or 'return' in er_lower:
                        lines.append("        # 验证返回数据")
                        lines.append("        data = assert_response_success(response)")
                        lines.append("        assert \"data\" in data")
                    
                    elif '登录' in name or 'login' in name.lower():
                        lines.append("        # 验证登录成功")
                        lines.append("        data = assert_response_success(response)")
                        lines.append("        assert \"token\" in data or \"access_token\" in data")
                    
                    else:
                        lines.append(f"        # 验证: {er}")
                        lines.append("        assert response.status_code == 200")
            
            if not lines:
                lines.append("        # 验证响应成功")
                lines.append("        assert_response_success(response)")
        
        return lines
    
    def _generate_api_test_class(self, api_endpoints: List[Dict[str, Any]]) -> str:
        """生成API测试类"""
        test_methods = []
        
        for i, endpoint in enumerate(api_endpoints):
            method = self._generate_api_test_method(endpoint, i)
            test_methods.append(method)
        
        return FUNCTIONAL_TEST_CLASS.format(
            class_name="API",
            description=f"API端点测试，包含 {len(api_endpoints)} 个端点测试",
            test_count=len(api_endpoints),
            test_methods="\n".join(test_methods)
        )
    
    def _generate_api_test_method(self, endpoint: Dict[str, Any], index: int) -> str:
        """生成API测试方法"""
        
        path = endpoint.get('path', '/api/endpoint')
        http_method = endpoint.get('method', 'get').lower()
        description = endpoint.get('description', f'测试 {path}')
        
        # 生成方法名
        method_name = f"api_{path.replace('/', '_').strip('_')}_{index}"
        
        # 生成payload
        if http_method in ['post', 'put', 'patch']:
            payload = "{\n            \"key\": \"value\"\n        }"
        else:
            payload = "None"
        
        # 生成断言字段
        assert_fields = '"code", "data"'
        
        return API_TEST_METHOD.format(
            method_name=method_name,
            extra_params="",
            docstring=description,
            endpoint=path,
            payload=payload,
            http_method=http_method,
            expected_status=200,
            assert_fields=assert_fields
        )
    
    def _group_test_cases(self, test_cases: List[Dict[str, Any]]) -> Dict[str, List]:
        """按测试类型分组"""
        grouped = {}
        for tc in test_cases:
            test_type = tc.get('test_type', '功能测试')
            class_name = f"Test{test_type.replace('测试', '')}"
            if class_name not in grouped:
                grouped[class_name] = []
            grouped[class_name].append(tc)
        return grouped


def generate_unified_test_code(test_cases: List[Dict[str, Any]], 
                              output_dir: str,
                              project_type: str = "unknown",
                              base_url: str = "http://localhost:8080",
                              api_prefix: str = "/api",
                              api_endpoints: List[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    生成统一测试代码的便捷函数
    
    Args:
        test_cases: 测试用例列表
        output_dir: 输出目录
        project_type: 项目类型
        base_url: 服务地址
        api_prefix: API前缀
        api_endpoints: API端点列表
        
    Returns:
        生成的文件路径字典
    """
    generator = UnifiedTestGenerator(project_type, base_url, api_prefix)
    return generator.generate(test_cases, output_dir, api_endpoints)


def main():
    parser = argparse.ArgumentParser(description='生成统一测试代码')
    parser.add_argument('input', help='输入测试用例JSON文件路径')
    parser.add_argument('--output', '-o', default='./generated_tests', 
                       help='输出目录（默认: ./generated_tests）')
    parser.add_argument('--project-type', '-p', default='unknown',
                       help='项目类型 (java-spring/python-flask/node-express)')
    parser.add_argument('--base-url', '-b', default='http://localhost:8080',
                       help='服务基础地址')
    parser.add_argument('--api-prefix', '-a', default='/api',
                       help='API前缀')
    
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
        files = generate_unified_test_code(
            test_cases, 
            args.output,
            project_type=args.project_type,
            base_url=args.base_url,
            api_prefix=args.api_prefix
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
