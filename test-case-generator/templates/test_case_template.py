#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用例模板生成器
用于生成标准化的测试用例模板
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime


def create_test_case_template(
    test_id: str,
    name: str,
    description: str,
    priority: str = "中",
    test_type: str = "功能测试",
    preconditions: List[str] = None,
    steps: List[str] = None,
    expected_results: List[str] = None,
    test_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    创建测试用例模板
    
    Args:
        test_id: 测试用例ID
        name: 测试用例名称
        description: 测试用例描述
        priority: 优先级（高/中/低）
        test_type: 测试类型
        preconditions: 前置条件列表
        steps: 测试步骤列表
        expected_results: 预期结果列表
        test_data: 测试数据
        
    Returns:
        测试用例字典
    """
    return {
        "id": test_id,
        "name": name,
        "description": description,
        "priority": priority,
        "test_type": test_type,
        "preconditions": preconditions or [],
        "steps": steps or [],
        "expected_results": expected_results or [],
        "test_data": test_data or {}
    }


def create_functional_test_case(
    test_id: str,
    feature_name: str,
    description: str = "",
    preconditions: List[str] = None,
    steps: List[str] = None,
    expected_results: List[str] = None
) -> Dict[str, Any]:
    """
    创建功能测试用例模板
    
    Args:
        test_id: 测试用例ID
        feature_name: 功能名称
        description: 测试描述
        preconditions: 前置条件
        steps: 测试步骤
        expected_results: 预期结果
        
    Returns:
        功能测试用例字典
    """
    if not description:
        description = f"验证{feature_name}功能是否正常工作"
    
    if not steps:
        steps = [
            "1. 启动系统",
            f"2. 执行{feature_name}操作",
            "3. 验证功能是否正常"
        ]
    
    if not expected_results:
        expected_results = [
            f"{feature_name}功能正常执行",
            "返回预期结果",
            "无异常错误"
        ]
    
    return create_test_case_template(
        test_id=test_id,
        name=f"功能测试 - {feature_name}",
        description=description,
        priority="高",
        test_type="功能测试",
        preconditions=preconditions or ["系统正常运行", "用户已登录"],
        steps=steps,
        expected_results=expected_results
    )


def create_boundary_test_case(
    test_id: str,
    feature_name: str,
    boundary_type: str = "边界值",
    description: str = "",
    preconditions: List[str] = None,
    steps: List[str] = None,
    expected_results: List[str] = None
) -> Dict[str, Any]:
    """
    创建边界测试用例模板
    
    Args:
        test_id: 测试用例ID
        feature_name: 功能名称
        boundary_type: 边界类型
        description: 测试描述
        preconditions: 前置条件
        steps: 测试步骤
        expected_results: 预期结果
        
    Returns:
        边界测试用例字典
    """
    if not description:
        description = f"验证{feature_name}在{boundary_type}条件下的行为"
    
    if not steps:
        steps = [
            "1. 准备边界测试数据",
            f"2. 在{boundary_type}条件下执行{feature_name}",
            "3. 验证系统行为"
        ]
    
    if not expected_results:
        expected_results = [
            "系统正确处理边界值",
            "返回适当的响应",
            "系统保持稳定"
        ]
    
    return create_test_case_template(
        test_id=test_id,
        name=f"边界测试 - {feature_name} - {boundary_type}",
        description=description,
        priority="中",
        test_type="边界测试",
        preconditions=preconditions or ["系统正常运行"],
        steps=steps,
        expected_results=expected_results
    )


def create_exception_test_case(
    test_id: str,
    feature_name: str,
    exception_scenario: str = "异常输入",
    description: str = "",
    preconditions: List[str] = None,
    steps: List[str] = None,
    expected_results: List[str] = None
) -> Dict[str, Any]:
    """
    创建异常测试用例模板
    
    Args:
        test_id: 测试用例ID
        feature_name: 功能名称
        exception_scenario: 异常场景
        description: 测试描述
        preconditions: 前置条件
        steps: 测试步骤
        expected_results: 预期结果
        
    Returns:
        异常测试用例字典
    """
    if not description:
        description = f"验证{feature_name}在{exception_scenario}时的处理能力"
    
    if not steps:
        steps = [
            f"1. 构造{exception_scenario}条件",
            f"2. 执行{feature_name}操作",
            "3. 验证异常处理"
        ]
    
    if not expected_results:
        expected_results = [
            "系统捕获异常",
            "返回友好的错误提示",
            "系统不崩溃"
        ]
    
    return create_test_case_template(
        test_id=test_id,
        name=f"异常测试 - {feature_name} - {exception_scenario}",
        description=description,
        priority="中",
        test_type="异常测试",
        preconditions=preconditions or ["系统正常运行"],
        steps=steps,
        expected_results=expected_results
    )


def create_test_suite(
    suite_name: str,
    test_cases: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    创建测试套件
    
    Args:
        suite_name: 测试套件名称
        test_cases: 测试用例列表
        
    Returns:
        测试套件字典
    """
    summary = {
        "total": len(test_cases),
        "by_priority": {},
        "by_type": {}
    }
    
    for tc in test_cases:
        # 统计优先级
        priority = tc.get("priority", "中")
        summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
        
        # 统计测试类型
        test_type = tc.get("test_type", "功能测试")
        summary["by_type"][test_type] = summary["by_type"].get(test_type, 0) + 1
    
    return {
        "suite_name": suite_name,
        "created_at": datetime.now().isoformat(),
        "test_cases": test_cases,
        "summary": summary
    }


def save_test_suite(test_suite: Dict[str, Any], output_path: str) -> None:
    """
    保存测试套件到文件
    
    Args:
        test_suite: 测试套件字典
        output_path: 输出文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(test_suite, f, ensure_ascii=False, indent=2)
    print(f"✓ 测试套件已保存到: {output_path}")


# 示例用法
if __name__ == '__main__':
    # 创建示例测试套件
    test_cases = [
        create_functional_test_case(
            "TC001",
            "用户登录",
            preconditions=["用户已注册", "系统正常运行"],
            steps=[
                "1. 打开登录页面",
                "2. 输入用户名和密码",
                "3. 点击登录按钮"
            ],
            expected_results=[
                "成功跳转到首页",
                "显示用户信息",
                "无错误提示"
            ]
        ),
        create_boundary_test_case(
            "TC002",
            "用户登录",
            boundary_type="空值输入",
            steps=[
                "1. 打开登录页面",
                "2. 不输入用户名和密码",
                "3. 点击登录按钮"
            ],
            expected_results=[
                "显示错误提示",
                "不跳转页面",
                "保持登录页面"
            ]
        ),
        create_exception_test_case(
            "TC003",
            "用户登录",
            exception_scenario="密码错误",
            steps=[
                "1. 打开登录页面",
                "2. 输入正确的用户名和错误的密码",
                "3. 点击登录按钮"
            ],
            expected_results=[
                "显示密码错误提示",
                "不跳转页面",
                "记录错误日志"
            ]
        )
    ]
    
    # 创建测试套件
    test_suite = create_test_suite("用户登录测试套件", test_cases)
    
    # 保存测试套件
    save_test_suite(test_suite, "test_suite_template.json")
    
    print("\n示例测试套件已生成！")
