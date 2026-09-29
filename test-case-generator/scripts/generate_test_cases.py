#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用例生成模块
基于解析的需求内容生成结构化的测试用例
"""

import json
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TestPriority(Enum):
    """测试优先级"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class TestType(Enum):
    """测试类型"""
    FUNCTIONAL = "功能测试"
    BOUNDARY = "边界测试"
    EXCEPTION = "异常测试"
    PERFORMANCE = "性能测试"
    SECURITY = "安全测试"
    COMPATIBILITY = "兼容性测试"


@dataclass
class TestCase:
    """测试用例数据类"""
    id: str
    name: str
    description: str
    priority: str
    test_type: str
    preconditions: List[str]
    steps: List[str]
    expected_results: List[str]
    test_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


def generate_test_case_id(index: int) -> str:
    """生成测试用例ID"""
    return f"TC{index:03d}"


def analyze_functional_requirements(content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    分析功能需求，提取测试点
    
    Args:
        content: 解析后的文档内容
        
    Returns:
        测试点列表
    """
    test_points = []
    
    # 从段落中提取功能描述
    for para in content.get("paragraphs", []):
        if len(para) > 10:
            # 分析段落内容，提取具体的功能点
            extracted = extract_functional_points(para)
            test_points.extend(extracted)
    
    # 从章节中提取功能描述
    for section in content.get("sections", []):
        section_title = section.get("title", "")
        if section.get("content"):
            for line in section["content"]:
                if len(line) > 10:
                    extracted = extract_functional_points(line, section_title)
                    test_points.extend(extracted)
    
    return test_points


def extract_functional_points(text: str, context: str = "") -> List[Dict[str, Any]]:
    """
    从文本中提取具体的功能点
    
    Args:
        text: 文本内容
        context: 上下文（如章节标题）
        
    Returns:
        功能点列表
    """
    points = []
    
    # 分析文本，提取动词和名词
    verbs = ['登录', '注册', '查询', '添加', '修改', '删除', '验证', '发送', '接收', '计算', '处理']
    nouns = ['用户', '订单', '商品', '支付', '消息', '邮件', '数据', '文件', '系统']
    
    # 匹配功能点
    for verb in verbs:
        for noun in nouns:
            if verb in text and noun in text:
                points.append({
                    "type": "functional",
                    "content": text,
                    "action": verb,
                    "object": noun,
                    "context": context,
                    "source": "extracted"
                })
                break
    
    # 如果没有匹配到具体功能点，添加通用功能点
    if not points and len(text) > 15:
        points.append({
            "type": "functional",
            "content": text,
            "action": "处理",
            "object": "数据",
            "context": context,
            "source": "general"
        })
    
    return points


def generate_functional_test_cases(test_points: List[Dict[str, Any]]) -> List[TestCase]:
    """
    基于功能测试点生成测试用例
    
    Args:
        test_points: 功能测试点列表
        
    Returns:
        测试用例列表
    """
    test_cases = []
    
    for i, point in enumerate(test_points, 1):
        action = point.get('action', '处理')
        object_name = point.get('object', '数据')
        context = point.get('context', '')
        
        # 生成类名和方法名
        class_name = f"{object_name}Service"
        method_name = f"{action}{object_name}"
        
        # 正常流程测试用例
        test_case = TestCase(
            id=generate_test_case_id(i),
            name=f"{action}{object_name}功能测试",
            description=f"验证{class_name}.{method_name}方法是否正常工作",
            priority=TestPriority.HIGH.value,
            test_type=TestType.FUNCTIONAL.value,
            preconditions=[f"{class_name}已初始化", "测试环境正常"],
            steps=[
                f"1. 调用{class_name}.{method_name}方法",
                f"2. 验证返回结果",
                f"3. 检查{object_name}状态"
            ],
            expected_results=[
                f"{action}{object_name}操作成功",
                "返回预期结果",
                "无异常错误"
            ]
        )
        test_cases.append(test_case)
        
        # 边界值测试用例
        boundary_test = TestCase(
            id=generate_test_case_id(i + 100),
            name=f"{action}{object_name}边界测试",
            description=f"验证{class_name}.{method_name}方法的边界条件处理",
            priority=TestPriority.MEDIUM.value,
            test_type=TestType.BOUNDARY.value,
            preconditions=[f"{class_name}已初始化"],
            steps=[
                f"1. 准备边界测试数据（空值、最大值、最小值）",
                f"2. 调用{class_name}.{method_name}方法",
                f"3. 验证系统行为"
            ],
            expected_results=[
                "系统正确处理边界值",
                "返回适当的错误提示或默认值",
                "系统保持稳定"
            ]
        )
        test_cases.append(boundary_test)
        
        # 异常测试用例
        exception_test = TestCase(
            id=generate_test_case_id(i + 200),
            name=f"{action}{object_name}异常测试",
            description=f"验证{class_name}.{method_name}方法的异常处理能力",
            priority=TestPriority.MEDIUM.value,
            test_type=TestType.EXCEPTION.value,
            preconditions=[f"{class_name}已初始化"],
            steps=[
                f"1. 构造异常输入或条件",
                f"2. 调用{class_name}.{method_name}方法",
                f"3. 验证异常处理"
            ],
            expected_results=[
                "系统捕获异常",
                "返回友好的错误提示",
                "系统不崩溃"
            ]
        )
        test_cases.append(exception_test)
    
    return test_cases


def generate_test_cases_from_content(content: Dict[str, Any]) -> List[TestCase]:
    """
    从文档内容生成完整的测试用例集
    
    Args:
        content: 解析后的文档内容
        
    Returns:
        测试用例列表
    """
    # 分析功能需求
    test_points = analyze_functional_requirements(content)
    
    # 生成测试用例
    test_cases = generate_functional_test_cases(test_points)
    
    return test_cases


def generate_test_cases_json(test_cases: List[TestCase]) -> str:
    """
    生成测试用例JSON
    
    Args:
        test_cases: 测试用例列表
        
    Returns:
        JSON字符串
    """
    data = {
        "test_cases": [tc.to_dict() for tc in test_cases],
        "summary": {
            "total": len(test_cases),
            "by_priority": {},
            "by_type": {}
        }
    }
    
    # 统计信息
    for tc in test_cases:
        # 按优先级统计
        priority = tc.priority
        data["summary"]["by_priority"][priority] = data["summary"]["by_priority"].get(priority, 0) + 1
        
        # 按类型统计
        test_type = tc.test_type
        data["summary"]["by_type"][test_type] = data["summary"]["by_type"].get(test_type, 0) + 1
    
    return json.dumps(data, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='生成测试用例')
    parser.add_argument('input', help='输入文件路径（解析后的JSON文件或需求文档）')
    parser.add_argument('--output', '-o', help='输出测试用例JSON文件路径')
    parser.add_argument('--format', choices=['json', 'markdown'], 
                       default='json', help='输出格式')
    
    args = parser.parse_args()
    
    try:
        # 读取输入文件
        with open(args.input, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # 如果输入是多个文件的结果，合并内容
        if isinstance(content, dict) and any(isinstance(v, dict) and "content" in v for v in content.values()):
            merged_content = {"paragraphs": [], "sections": [], "tables": []}
            for file_result in content.values():
                if isinstance(file_result, dict) and file_result.get("status") == "success":
                    file_content = file_result["content"]
                    merged_content["paragraphs"].extend(file_content.get("paragraphs", []))
                    merged_content["sections"].extend(file_content.get("sections", []))
                    merged_content["tables"].extend(file_content.get("tables", []))
            content = merged_content
        
        # 生成测试用例
        test_cases = generate_test_cases_from_content(content)
        
        # 输出结果
        if args.format == 'json':
            output = generate_test_cases_json(test_cases)
        else:
            # Markdown格式
            output_parts = ["# 测试用例文档\n"]
            for tc in test_cases:
                output_parts.append(f"## {tc.id}: {tc.name}\n")
                output_parts.append(f"- **优先级**: {tc.priority}")
                output_parts.append(f"- **类型**: {tc.test_type}")
                output_parts.append(f"- **描述**: {tc.description}\n")
                output_parts.append("**前置条件:**")
                for pre in tc.preconditions:
                    output_parts.append(f"- {pre}")
                output_parts.append("\n**测试步骤:**")
                for step in tc.steps:
                    output_parts.append(f"- {step}")
                output_parts.append("\n**预期结果:**")
                for result in tc.expected_results:
                    output_parts.append(f"- {result}")
                output_parts.append("\n---\n")
            output = "\n".join(output_parts)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✓ 测试用例已保存到: {args.output}")
        else:
            print(output)
        
        print(f"\n✓ 共生成 {len(test_cases)} 个测试用例")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
