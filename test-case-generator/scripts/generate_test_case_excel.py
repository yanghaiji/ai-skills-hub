#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Excel测试用例生成模块
将测试用例导出为Excel格式
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def check_openpyxl_installed() -> bool:
    """检查openpyxl是否已安装"""
    try:
        import openpyxl
        return True
    except ImportError:
        return False


def install_openpyxl():
    """安装openpyxl"""
    import subprocess
    import sys
    print("正在安装openpyxl...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "openpyxl"], 
                      check=True, capture_output=True)
        print("✓ openpyxl安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ openpyxl安装失败: {e}")
        return False


def create_test_case_excel(test_cases: List[Dict[str, Any]], 
                          output_path: str,
                          sheet_name: str = "测试用例") -> None:
    """
    创建Excel测试用例文件
    
    Args:
        test_cases: 测试用例列表
        output_path: 输出文件路径
        sheet_name: 工作表名称
    """
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    
    # 创建工作簿
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    
    # 定义样式
    header_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    cell_font = Font(name='微软雅黑', size=10)
    cell_alignment = Alignment(vertical='center', wrap_text=True)
    
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # 定义表头
    headers = [
        '测试用例ID', '测试用例名称', '测试描述', '优先级', '测试类型',
        '前置条件', '测试步骤', '预期结果', '测试数据', '状态', '备注'
    ]
    
    # 设置列宽
    column_widths = [12, 30, 40, 8, 12, 25, 40, 40, 30, 10, 20]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[chr(64 + i)].width = width
    
    # 写入表头
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # 写入测试用例数据
    for row_idx, tc in enumerate(test_cases, 2):
        # 格式化列表字段为字符串
        preconditions = '\n'.join(tc.get('preconditions', []))
        steps = '\n'.join(tc.get('steps', []))
        expected_results = '\n'.join(tc.get('expected_results', []))
        test_data = json.dumps(tc.get('test_data', {}), ensure_ascii=False, indent=2) if tc.get('test_data') else ''
        
        row_data = [
            tc.get('id', ''),
            tc.get('name', ''),
            tc.get('description', ''),
            tc.get('priority', ''),
            tc.get('test_type', ''),
            preconditions,
            steps,
            expected_results,
            test_data,
            '待执行',
            ''
        ]
        
        for col, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col, value=value)
            cell.font = cell_font
            cell.alignment = cell_alignment
            cell.border = thin_border
            
            # 根据优先级设置颜色
            if col == 4:  # 优先级列
                if value == '高':
                    cell.fill = PatternFill(start_color='FF6B6B', end_color='FF6B6B', fill_type='solid')
                    cell.font = Font(name='微软雅黑', size=10, bold=True, color='FFFFFF')
                elif value == '中':
                    cell.fill = PatternFill(start_color='FFD93D', end_color='FFD93D', fill_type='solid')
                    cell.font = Font(name='微软雅黑', size=10, bold=True)
                elif value == '低':
                    cell.fill = PatternFill(start_color='6BCB77', end_color='6BCB77', fill_type='solid')
                    cell.font = Font(name='微软雅黑', size=10, bold=True)
            
            # 根据测试类型设置颜色
            if col == 5:  # 测试类型列
                if value == '功能测试':
                    cell.fill = PatternFill(start_color='4D96FF', end_color='4D96FF', fill_type='solid')
                    cell.font = Font(name='微软雅黑', size=10, color='FFFFFF')
                elif value == '边界测试':
                    cell.fill = PatternFill(start_color='9B59B6', end_color='9B59B6', fill_type='solid')
                    cell.font = Font(name='微软雅黑', size=10, color='FFFFFF')
                elif value == '异常测试':
                    cell.fill = PatternFill(start_color='E74C3C', end_color='E74C3C', fill_type='solid')
                    cell.font = Font(name='微软雅黑', size=10, color='FFFFFF')
    
    # 冻结首行
    ws.freeze_panes = 'A2'
    
    # 设置自动筛选
    ws.auto_filter.ref = f"A1:K{len(test_cases) + 1}"
    
    # 保存文件
    wb.save(output_path)
    print(f"✓ Excel测试用例已保存到: {output_path}")


def create_summary_sheet(test_cases: List[Dict[str, Any]], 
                        wb) -> None:
    """
    创建统计摘要工作表
    
    Args:
        test_cases: 测试用例列表
        wb: 工作簿对象
    """
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.chart import PieChart, Reference
    
    # 创建摘要工作表
    ws_summary = wb.create_sheet("统计摘要", 0)
    
    # 统计数据
    total = len(test_cases)
    by_priority = {}
    by_type = {}
    
    for tc in test_cases:
        priority = tc.get('priority', '中')
        test_type = tc.get('test_type', '功能测试')
        
        by_priority[priority] = by_priority.get(priority, 0) + 1
        by_type[test_type] = by_type.get(test_type, 0) + 1
    
    # 标题样式
    title_font = Font(name='微软雅黑', size=14, bold=True, color='2C3E50')
    header_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='3498DB', end_color='3498DB', fill_type='solid')
    
    # 写入标题
    ws_summary['A1'] = '测试用例统计摘要'
    ws_summary['A1'].font = title_font
    ws_summary.merge_cells('A1:D1')
    
    ws_summary['A2'] = f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    ws_summary['A2'].font = Font(name='微软雅黑', size=10, color='7F8C8D')
    
    # 总体统计
    ws_summary['A4'] = '总体统计'
    ws_summary['A4'].font = Font(name='微软雅黑', size=12, bold=True)
    
    ws_summary['A5'] = '测试用例总数'
    ws_summary['B5'] = total
    ws_summary['A5'].font = Font(name='微软雅黑', size=10, bold=True)
    ws_summary['B5'].font = Font(name='微软雅黑', size=10)
    
    # 按优先级统计
    ws_summary['A7'] = '按优先级统计'
    ws_summary['A7'].font = Font(name='微软雅黑', size=12, bold=True)
    
    # 表头
    for col, header in enumerate(['优先级', '数量', '占比'], 1):
        cell = ws_summary.cell(row=8, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
    
    row = 9
    for priority, count in sorted(by_priority.items()):
        ws_summary.cell(row=row, column=1, value=priority)
        ws_summary.cell(row=row, column=2, value=count)
        ws_summary.cell(row=row, column=3, value=f"{count/total*100:.1f}%")
        row += 1
    
    # 按测试类型统计
    ws_summary['A' + str(row + 1)] = '按测试类型统计'
    ws_summary['A' + str(row + 1)].font = Font(name='微软雅黑', size=12, bold=True)
    
    # 表头
    for col, header in enumerate(['测试类型', '数量', '占比'], 1):
        cell = ws_summary.cell(row=row + 2, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
    
    row += 3
    for test_type, count in sorted(by_type.items()):
        ws_summary.cell(row=row, column=1, value=test_type)
        ws_summary.cell(row=row, column=2, value=count)
        ws_summary.cell(row=row, column=3, value=f"{count/total*100:.1f}%")
        row += 1
    
    # 设置列宽
    ws_summary.column_dimensions['A'].width = 20
    ws_summary.column_dimensions['B'].width = 15
    ws_summary.column_dimensions['C'].width = 15


def main():
    parser = argparse.ArgumentParser(description='生成Excel测试用例')
    parser.add_argument('input', help='输入测试用例JSON文件路径')
    parser.add_argument('--output', '-o', default='./test_cases.xlsx', 
                       help='输出Excel文件路径（默认: ./test_cases.xlsx）')
    parser.add_argument('--sheet', '-s', default='测试用例', 
                       help='工作表名称（默认: 测试用例）')
    parser.add_argument('--summary', action='store_true', 
                       help='包含统计摘要工作表')
    
    args = parser.parse_args()
    
    # 检查openpyxl是否安装
    if not check_openpyxl_installed():
        if not install_openpyxl():
            return 1
    
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
        
        # 创建Excel文件
        import openpyxl
        wb = openpyxl.Workbook()
        
        # 添加统计摘要（如果需要）
        if args.summary:
            create_summary_sheet(test_cases, wb)
        
        # 创建测试用例工作表
        if args.summary:
            ws = wb.active
            ws.title = args.sheet
        else:
            ws = wb.active
            ws.title = args.sheet
        
        # 重新创建测试用例工作表
        create_test_case_excel(test_cases, args.output, args.sheet)
        
        print(f"\n✓ 共导出 {len(test_cases)} 个测试用例")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
