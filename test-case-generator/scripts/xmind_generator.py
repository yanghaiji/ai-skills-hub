#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
XMind思维导图生成模块
生成测试策略全景视图：测试概览 + 关键业务链路 + 功能模块 + 专项测试
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import zipfile
import os


def _make_topic(id: str, title: str, children: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """创建思维导图节点"""
    topic = {
        "id": id,
        "class": "topic",
        "title": title
    }
    if children:
        topic["children"] = {"attached": children}
    return topic


def generate_xmind_content(
    test_cases: List[Dict[str, Any]],
    title: str = "测试策略",
    doc_title: str = ""
) -> List[Dict[str, Any]]:
    """
    生成XMind策略全景结构

    结构：
    -  测试概览（范围、策略、风险）
    -  关键业务链路（核心端到端流程）
    - 📦 功能模块测试（按模块分组）
    - ⚙️ 专项测试（性能/安全/兼容性）

    Args:
        test_cases: 测试用例列表
        title: 思维导图标题
        doc_title: 需求文档标题

    Returns:
        XMind content.json 内容
    """
    project_name = doc_title or "项目"

    # ── 按测试类型分组 ──
    functional_cases = [tc for tc in test_cases if tc.get('test_type') == '功能测试']
    boundary_cases = [tc for tc in test_cases if tc.get('test_type') == '边界测试']
    exception_cases = [tc for tc in test_cases if tc.get('test_type') == '异常测试']
    performance_cases = [tc for tc in test_cases if tc.get('test_type') == '性能测试']
    security_cases = [tc for tc in test_cases if tc.get('test_type') == '安全测试']

    # ── 按模块分组（从测试用例名称中提取） ──
    module_groups: Dict[str, List[Dict]] = {}
    for tc in test_cases:
        name = tc.get('name', '')
        # 尝试从名称中提取模块（取前几个字作为模块标识）
        module = _extract_module(name)
        if module not in module_groups:
            module_groups[module] = []
        module_groups[module].append(tc)

    # ─ 构建根节点 ──
    root_children = []

    # 1. 测试概览
    root_children.append(_build_overview(project_name, test_cases))

    # 2. 关键业务链路（从功能测试用例中提取）
    root_children.append(_build_key_chains(functional_cases, boundary_cases, exception_cases))

    # 3. 功能模块测试
    root_children.append(_build_module_tests(module_groups))

    # 4. 专项测试
    root_children.append(_build_specialized_tests(performance_cases, security_cases, boundary_cases, exception_cases))

    root_topic = {
        "id": "root",
        "class": "topic",
        "title": f"{project_name} 测试策略",
        "structureClass": "org.xmind.ui.map.unbalanced",
        "children": {"attached": root_children}
    }

    return [{
        "id": "sheet_1",
        "class": "sheet",
        "title": f"{project_name} 测试策略",
        "rootTopic": root_topic
    }]


def _extract_module(name: str) -> str:
    """
    从测试用例名称中提取模块名
    策略：取名称中第一个动词前的名词部分，或前4个字符
    """
    # 常见动词列表
    verbs = ['登录', '注册', '查询', '添加', '修改', '删除', '提交', '审核',
             '创建', '更新', '导入', '导出', '下载', '上传', '发送', '接收',
             '验证', '处理', '计算', '解析', '同步', '通知']
    for verb in verbs:
        idx = name.find(verb)
        if idx > 0:
            return name[:idx].strip()
    # 默认取前4个字符
    return name[:4].strip() if name else "未知模块"


def _build_overview(project_name: str, test_cases: List[Dict]) -> Dict[str, Any]:
    """构建测试概览节点"""
    total = len(test_cases)
    high = sum(1 for tc in test_cases if tc.get('priority') == '高')
    medium = sum(1 for tc in test_cases if tc.get('priority') == '中')
    low = sum(1 for tc in test_cases if tc.get('priority') == '低')

    return _make_topic("overview", "📋 测试概览", [
        _make_topic("ov_scope", "测试范围", [
            _make_topic("ov_scope_1", f"共 {total} 个测试用例"),
            _make_topic("ov_scope_2", f"高优先级: {high} 个"),
            _make_topic("ov_scope_3", f"中优先级: {medium} 个"),
            _make_topic("ov_scope_4", f"低优先级: {low} 个"),
        ]),
        _make_topic("ov_strategy", "测试策略", [
            _make_topic("ov_strat_1", "功能测试：覆盖核心业务流程"),
            _make_topic("ov_strat_2", "边界测试：验证极限值和异常输入"),
            _make_topic("ov_strat_3", "异常测试：确保系统容错能力"),
        ]),
        _make_topic("ov_risk", "风险评估", [
            _make_topic("ov_risk_1", "⚠️ 高优先级用例需优先执行"),
            _make_topic("ov_risk_2", "⚠️ 关注边界和异常场景的覆盖率"),
        ]),
    ])


def _build_key_chains(
    functional: List[Dict],
    boundary: List[Dict],
    exception: List[Dict]
) -> Dict[str, Any]:
    """构建关键业务链路节点"""
    chains = []

    # 按模块分组功能测试用例，每个模块视为一条链路
    module_groups: Dict[str, List[Dict]] = {}
    for tc in functional:
        module = _extract_module(tc.get('name', ''))
        if module not in module_groups:
            module_groups[module] = []
        module_groups[module].append(tc)

    for module, cases in module_groups.items():
        chain_children = []

        # 正常流程
        normal_steps = []
        for tc in cases:
            steps = tc.get('steps', [])
            if steps:
                normal_steps.append(_make_topic(
                    f"normal_{tc.get('id', '')}",
                    tc.get('name', '')
                ))
        if normal_steps:
            chain_children.append(_make_topic("normal_flow", "正常流程", normal_steps))

        # 异常分支（从异常测试用例中找同模块的）
        exception_children = []
        for tc in exception:
            tc_module = _extract_module(tc.get('name', ''))
            if tc_module == module:
                exception_children.append(_make_topic(
                    f"exc_{tc.get('id', '')}",
                    f"⚠️ {tc.get('name', '')}"
                ))
        if exception_children:
            chain_children.append(_make_topic("exception_flow", "异常分支", exception_children))

        # 边界条件
        boundary_children = []
        for tc in boundary:
            tc_module = _extract_module(tc.get('name', ''))
            if tc_module == module:
                boundary_children.append(_make_topic(
                    f"bound_{tc.get('id', '')}",
                    tc.get('name', '')
                ))
        if boundary_children:
            chain_children.append(_make_topic("boundary_flow", "边界条件", boundary_children))

        chains.append(_make_topic(f"chain_{module}", f"🔑 {module}", chain_children))

    if not chains:
        chains.append(_make_topic("chain_empty", "暂无关键链路数据"))

    return _make_topic("key_chains", "🔑 关键业务链路", chains)


def _build_module_tests(module_groups: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """构建功能模块测试节点"""
    module_topics = []

    for module, cases in module_groups.items():
        func_points = []
        for tc in cases:
            priority_mark = "" 
            p = tc.get('priority', '')
            if p == '高':
                priority_mark = ""
            elif p == '中':
                priority_mark = "🟡"
            else:
                priority_mark = "🟢"

            func_points.append(_make_topic(
                f"fp_{tc.get('id', '')}",
                f"{priority_mark} {tc.get('name', '')}"
            ))

        if func_points:
            module_topics.append(_make_topic(f"mod_{module}", f"📦 {module}", func_points))

    if not module_topics:
        module_topics.append(_make_topic("mod_empty", "暂无功能模块数据"))

    return _make_topic("module_tests", "📦 功能模块测试", module_topics)


def _build_specialized_tests(
    performance: List[Dict],
    security: List[Dict],
    boundary: List[Dict],
    exception: List[Dict]
) -> Dict[str, Any]:
    """构建专项测试节点"""
    children = []

    # 性能测试
    perf_children = []
    if performance:
        for tc in performance:
            perf_children.append(_make_topic(f"perf_{tc.get('id', '')}", tc.get('name', '')))
    else:
        perf_children.append(_make_topic("perf_hint", "根据业务场景补充性能测试点"))
    children.append(_make_topic("perf", "性能测试", perf_children))

    # 安全测试
    sec_children = []
    if security:
        for tc in security:
            sec_children.append(_make_topic(f"sec_{tc.get('id', '')}", tc.get('name', '')))
    else:
        sec_children.append(_make_topic("sec_hint", "根据业务场景补充安全测试点（SQL注入/XSS/越权）"))
    children.append(_make_topic("sec", "安全测试", sec_children))

    # 兼容性测试
    compat_children = [
        _make_topic("compat_1", "浏览器兼容性（Chrome/Firefox/Safari/Edge）"),
        _make_topic("compat_2", "移动端适配（iOS/Android）"),
        _make_topic("compat_3", "分辨率适配"),
    ]
    children.append(_make_topic("compat", "兼容性测试", compat_children))

    return _make_topic("specialized", "⚙️ 专项测试", children)


def generate_xmind_metadata() -> Dict[str, Any]:
    """生成XMind元数据"""
    return {
        "creator": {
            "name": "Test Case Generator",
            "version": "5.0.0"
        }
    }


def generate_xmind_manifest() -> Dict[str, Any]:
    """生成XMind清单文件"""
    return {
        "file-entries": {
            "content.json": {},
            "metadata.json": {}
        }
    }


def save_xmind(test_cases: List[Dict[str, Any]], 
               output_path: str,
               title: str = "测试策略",
               doc_title: str = "") -> str:
    """
    保存为XMind文件
    
    Args:
        test_cases: 测试用例列表
        output_path: 输出文件路径
        title: 思维导图标题
        doc_title: 需求文档标题（用作项目名称）
        
    Returns:
        保存的文件路径
    """
    output_path = Path(output_path)
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 生成内容
    content = generate_xmind_content(test_cases, title, doc_title)
    metadata = generate_xmind_metadata()
    manifest = generate_xmind_manifest()
    
    # 创建XMind文件（实际上是ZIP文件）
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 写入content.json
        zf.writestr('content.json', json.dumps(content, ensure_ascii=False, indent=2))
        
        # 写入metadata.json
        zf.writestr('metadata.json', json.dumps(metadata, ensure_ascii=False, indent=2))
        
        # 写入manifest.json
        zf.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    
    return str(output_path)


def create_xmind_from_test_cases(test_cases: List[Dict[str, Any]],
                                 output_path: str,
                                 title: str = None,
                                 doc_title: str = "") -> str:
    """
    从测试用例创建XMind文件的便捷函数
    
    Args:
        test_cases: 测试用例列表
        output_path: 输出文件路径
        title: 思维导图标题
        doc_title: 需求文档标题（用作项目名称）
        
    Returns:
        保存的文件路径
    """
    if not title:
        title = f"测试策略 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    return save_xmind(test_cases, output_path, title, doc_title)


def main():
    parser = argparse.ArgumentParser(description='生成XMind思维导图测试用例')
    parser.add_argument('input', help='输入测试用例JSON文件路径')
    parser.add_argument('--output', '-o', default='./test_cases.xmind', 
                       help='输出XMind文件路径（默认: ./test_cases.xmind）')
    parser.add_argument('--title', '-t', default='测试用例思维导图',
                       help='思维导图标题')
    
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
        
        # 生成XMind文件
        output_path = create_xmind_from_test_cases(
            test_cases, 
            args.output,
            args.title
        )
        
        print(f"✓ XMind思维导图已生成到: {output_path}")
        print(f"  共包含 {len(test_cases)} 个测试用例")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
