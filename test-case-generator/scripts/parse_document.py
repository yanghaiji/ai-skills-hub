#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文档解析模块
支持解析 .docx、.pdf、.md、.txt、.png、.jpg 格式的文档

解析策略（按优先级）：
1. 本地 AI 直接读取（如果 AI 支持该格式）
2. 使用相关 skill 的脚本读取
3. 使用本模块内置的 Python 脚本读取
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any


def parse_docx(file_path: str) -> Dict[str, Any]:
    """
    解析Word文档(.docx)
    
    Args:
        file_path: Word文档路径
        
    Returns:
        包含文档内容的字典
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("请先安装python-docx: pip install python-docx")
    
    doc = Document(file_path)
    
    content = {
        "title": "",
        "sections": [],
        "tables": [],
        "paragraphs": []
    }
    
    # 提取标题（第一个段落通常是标题）
    if doc.paragraphs:
        content["title"] = doc.paragraphs[0].text.strip()
    
    # 提取所有段落
    current_section = None
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        
        # 检测标题样式
        if para.style.name.startswith('Heading'):
            if current_section:
                content["sections"].append(current_section)
            current_section = {
                "title": text,
                "level": int(para.style.name.replace('Heading ', '')),
                "content": []
            }
        elif current_section:
            current_section["content"].append(text)
        else:
            content["paragraphs"].append(text)
    
    # 添加最后一个section
    if current_section:
        content["sections"].append(current_section)
    
    # 提取表格
    for table in doc.tables:
        table_data = []
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                row_data.append(cell.text.strip())
            table_data.append(row_data)
        content["tables"].append(table_data)
    
    return content


def parse_pdf(file_path: str) -> Dict[str, Any]:
    """
    解析PDF文档（完整降级链）
    
    解析策略（按优先级）：
    1. 使用 pdfplumber 提取文本（文本型PDF）
    2. 使用 OCR 识别文本（图片型PDF，需要pytesseract）
    3. 使用 pymupdf 直接提取（备用方案）
    4. 转换为图片，由AI读取（最后手段）
    
    Args:
        file_path: PDF文档路径
        
    Returns:
        包含文档内容的字典
    """
    content = {
        "title": "",
        "sections": [],
        "tables": [],
        "paragraphs": [],
        "source_type": "pdf"
    }
    
    # 策略1: 使用 pdfplumber 提取文本
    print("  [1/4] 尝试使用pdfplumber提取文本...")
    text_content = _parse_pdf_with_pdfplumber(file_path)
    
    has_text = (
        text_content.get("paragraphs") or 
        text_content.get("sections") or 
        text_content.get("tables")
    )
    
    if has_text:
        content.update(text_content)
        content["pdf_type"] = "text"
        content["extraction_method"] = "pdfplumber"
        print("  ✓ 文本提取成功")
        return content
    
    print("   文本提取失败，检测为图片型PDF")
    
    # 策略2: 使用 OCR 识别
    print("  [2/4] 尝试使用OCR识别文本...")
    ocr_content = _parse_pdf_with_ocr(file_path)
    
    if ocr_content:
        content.update(ocr_content)
        content["pdf_type"] = "ocr"
        content["extraction_method"] = "ocr"
        print("  ✓ OCR识别成功")
        return content
    
    print("  ⚠ OCR不可用或识别失败")
    
    # 策略3: 使用 pymupdf 直接提取
    print("  [3/4] 尝试使用pymupdf直接提取...")
    try:
        import pymupdf
        doc = pymupdf.open(file_path)
        
        for i, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                lines = text.strip().split('\n')
                if i == 0 and lines:
                    content["title"] = lines[0].strip()
                for line in lines:
                    line = line.strip()
                    if line:
                        content["paragraphs"].append(line)
        doc.close()
        
        if content["paragraphs"]:
            content["pdf_type"] = "image_with_text"
            content["extraction_method"] = "pymupdf"
            print("  ✓ pymupdf提取成功")
            return content
    except Exception as e:
        print(f"   pymupdf提取失败: {e}")
    
    # 策略4: 转换为图片，由AI读取
    print("  [4/4] 转换为图片，由AI读取...")
    image_content = _parse_pdf_to_images(file_path)
    content.update(image_content)
    content["pdf_type"] = "image"
    content["extraction_method"] = "ai_read"
    print("  ✓ 图片转换完成，请AI读取图片内容")
    
    return content


def _parse_pdf_with_pdfplumber(file_path: str) -> Dict[str, Any]:
    """
    使用 pdfplumber 解析PDF（文本型）
    
    Args:
        file_path: PDF文档路径
        
    Returns:
        包含文档内容的字典
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("请先安装pdfplumber: pip install pdfplumber")
    
    content = {
        "title": "",
        "sections": [],
        "tables": [],
        "paragraphs": []
    }
    
    with pdfplumber.open(file_path) as pdf:
        # 提取第一页作为标题（如果有的话）
        if pdf.pages:
            first_page_text = pdf.pages[0].extract_text()
            if first_page_text:
                lines = first_page_text.strip().split('\n')
                if lines:
                    content["title"] = lines[0].strip()
        
        # 提取所有页面的文本
        current_section = None
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 简单的标题检测（全大写或以数字开头）
                if line.isupper() or (len(line) > 2 and line[0].isdigit() and '.' in line[:5]):
                    if current_section:
                        content["sections"].append(current_section)
                    current_section = {
                        "title": line,
                        "level": 1,
                        "content": []
                    }
                elif current_section:
                    current_section["content"].append(line)
                else:
                    content["paragraphs"].append(line)
            
            # 提取表格
            tables = page.extract_tables()
            for table in tables:
                if table:
                    content["tables"].append(table)
    
    # 添加最后一个section
    if current_section:
        content["sections"].append(current_section)
    
    return content


def _parse_pdf_with_ocr(file_path: str) -> Optional[Dict[str, Any]]:
    """
    使用 OCR 识别PDF中的文本（图片型PDF）
    
    尝试多种OCR方案：
    1. pytesseract + Tesseract OCR
    2. pymupdf 内置OCR（如果可用）
    3. 返回None，由调用方处理
    
    Args:
        file_path: PDF文档路径
        
    Returns:
        包含文档内容的字典，如果OCR不可用返回None
    """
    # 方案1: 尝试使用 pytesseract
    try:
        import pytesseract
        from PIL import Image
        import pymupdf
        
        # 检查Tesseract是否安装
        try:
            pytesseract.get_tesseract_version()
            print("   ✓ 检测到Tesseract OCR")
        except Exception:
            print("   ⚠ Tesseract OCR未安装，尝试其他方案...")
            raise Exception("Tesseract not installed")
        
        content = {
            "title": "",
            "sections": [],
            "tables": [],
            "paragraphs": []
        }
        
        doc = pymupdf.open(file_path)
        
        for i, page in enumerate(doc):
            # 将页面转换为图片
            pixmap = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            
            # OCR识别
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            
            if text.strip():
                lines = text.strip().split('\n')
                
                # 第一页第一行作为标题
                if i == 0 and lines and not content["title"]:
                    content["title"] = lines[0].strip()
                
                # 解析文本
                current_section = None
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.isupper() or (len(line) > 2 and line[0].isdigit() and '.' in line[:5]):
                        if current_section:
                            content["sections"].append(current_section)
                        current_section = {
                            "title": line,
                            "level": 1,
                            "content": []
                        }
                    elif current_section:
                        current_section["content"].append(line)
                    else:
                        content["paragraphs"].append(line)
                
                if current_section:
                    content["sections"].append(current_section)
        
        doc.close()
        return content
        
    except Exception as e:
        print(f"   pytesseract方案失败: {e}")
    
    # 方案2: 尝试使用 pymupdf 直接提取（某些图片PDF可能有隐藏文本层）
    try:
        import pymupdf
        
        print("   尝试使用pymupdf直接提取...")
        content = {
            "title": "",
            "sections": [],
            "tables": [],
            "paragraphs": []
        }
        
        doc = pymupdf.open(file_path)
        
        for i, page in enumerate(doc):
            # 尝试提取文本（即使主要是图片，也可能有文本层）
            text = page.get_text("text")
            
            if text.strip():
                lines = text.strip().split('\n')
                
                if i == 0 and lines and not content["title"]:
                    content["title"] = lines[0].strip()
                
                for line in lines:
                    line = line.strip()
                    if line:
                        content["paragraphs"].append(line)
        
        doc.close()
        
        # 如果提取到了内容，返回
        if content["paragraphs"]:
            print("   ✓ pymupdf提取到文本内容")
            return content
        
    except Exception as e:
        print(f"   pymupdf提取失败: {e}")
    
    return None


def _parse_pdf_to_images(file_path: str) -> Dict[str, Any]:
    """
    将PDF转换为图片，供AI读取
    
    Args:
        file_path: PDF文档路径
        
    Returns:
        包含图片路径的字典
    """
    try:
        import pymupdf
    except ImportError:
        print("   安装pymupdf...")
        os.system(f"{sys.executable} -m pip install pymupdf -q")
        import pymupdf
    
    content = {
        "title": "",
        "sections": [],
        "tables": [],
        "paragraphs": [],
        "images": []
    }
    
    doc = pymupdf.open(file_path)
    output_dir = Path(file_path).parent / "_pdf_images_temp"
    output_dir.mkdir(exist_ok=True)
    
    try:
        for i, page in enumerate(doc):
            pixmap = page.get_pixmap(dpi=200)
            image_path = output_dir / f"page_{i+1}.png"
            pixmap.save(str(image_path))
            content["images"].append(str(image_path))
            print(f"   ✓ 第{i+1}页 → {image_path.name}")
    finally:
        doc.close()
    
    content["note"] = f"已生成{len(content['images'])}张图片，请AI读取图片内容后生成测试用例"
    
    return content


def parse_markdown(file_path: str) -> Dict[str, Any]:
    """
    解析Markdown文档
    
    Args:
        file_path: Markdown文档路径
        
    Returns:
        包含文档内容的字典
    """
    content = {
        "title": "",
        "sections": [],
        "tables": [],
        "paragraphs": []
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_section = None
    in_code_block = False
    code_block_content = []
    table_rows = []
    
    for line in lines:
        line = line.rstrip('\n')
        
        # 处理代码块
        if line.strip().startswith('```'):
            if in_code_block:
                in_code_block = False
                # 代码块内容作为段落添加
                if code_block_content:
                    content["paragraphs"].append('\n'.join(code_block_content))
                code_block_content = []
            else:
                in_code_block = True
            continue
        
        if in_code_block:
            code_block_content.append(line)
            continue
        
        # 处理标题
        if line.startswith('#'):
            if current_section:
                content["sections"].append(current_section)
            
            level = len(line.split(' ')[0])
            title = line.lstrip('#').strip()
            current_section = {
                "title": title,
                "level": level,
                "content": []
            }
            continue
        
        # 处理表格行
        if '|' in line and line.strip().startswith('|'):
            # 跳过分隔行
            if set(line.replace('|', '').replace('-', '').replace(':', '').replace(' ', '')) == set():
                continue
            
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            table_rows.append(cells)
            continue
        elif table_rows:
            # 表格结束
            content["tables"].append(table_rows)
            table_rows = []
        
        # 处理普通段落
        stripped_line = line.strip()
        if stripped_line:
            if current_section:
                current_section["content"].append(stripped_line)
            else:
                content["paragraphs"].append(stripped_line)
    
    # 添加最后一个section
    if current_section:
        content["sections"].append(current_section)
    
    # 添加最后一个表格
    if table_rows:
        content["tables"].append(table_rows)
    
    return content


def parse_text(file_path: str) -> Dict[str, Any]:
    """
    解析纯文本文档
    
    Args:
        file_path: 文本文档路径
        
    Returns:
        包含文档内容的字典
    """
    content = {
        "title": "",
        "sections": [],
        "tables": [],
        "paragraphs": []
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_section = None
    for line in lines:
        line = line.rstrip('\n').strip()
        if not line:
            continue
        
        # 简单的标题检测（全大写或以数字开头）
        if line.isupper() or (len(line) > 2 and line[0].isdigit() and '.' in line[:5]):
            if current_section:
                content["sections"].append(current_section)
            current_section = {
                "title": line,
                "level": 1,
                "content": []
            }
        elif current_section:
            current_section["content"].append(line)
        else:
            content["paragraphs"].append(line)
    
    # 添加最后一个section
    if current_section:
        content["sections"].append(current_section)
    
    return content


def parse_image(file_path: str) -> Dict[str, Any]:
    """
    解析图片文档（.png、.jpg）
    
    解析策略：
    1. 验证图片文件有效性
    2. 返回文件路径供AI直接读取
    
    Args:
        file_path: 图片文件路径
        
    Returns:
        包含文档内容的字典
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("请先安装Pillow: pip install Pillow")
    
    content = {
        "title": "",
        "sections": [],
        "tables": [],
        "paragraphs": [],
        "source_type": "image",
        "file_path": file_path
    }
    
    # 验证图片并提取元数据
    try:
        img = Image.open(file_path)
        content["image_info"] = {
            "format": img.format,
            "size": list(img.size),
            "mode": img.mode
        }
        img.close()
        print(f"  ✓ 图片信息：{img.format}, {img.size[0]}x{img.size[1]}")
    except Exception as e:
        raise ValueError(f"无法打开图片文件：{e}")
    
    content["note"] = "图片文件，请AI直接读取文件内容后生成测试用例"
    
    return content


def parse_document(file_path: str) -> Dict[str, Any]:
    """
    根据文件扩展名选择合适的解析器
    
    支持的格式：
    - .docx - Word文档
    - .pdf  - PDF文档（支持文本型和图片型）
    - .md   - Markdown文档
    - .txt  - 纯文本文档
    - .png  - PNG图片
    - .jpg  - JPEG图片
    
    Args:
        file_path: 文档路径
        
    Returns:
        包含文档内容的字典
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    suffix = file_path.suffix.lower()
    
    parsers = {
        '.docx': parse_docx,
        '.pdf': parse_pdf,
        '.md': parse_markdown,
        '.txt': parse_text,
        '.png': parse_image,
        '.jpg': parse_image,
        '.jpeg': parse_image
    }
    
    if suffix not in parsers:
        raise ValueError(f"不支持的文件格式: {suffix}。支持的格式: {', '.join(parsers.keys())}")
    
    return parsers[suffix](str(file_path))


def format_content_for_ai(content: Dict[str, Any]) -> str:
    """
    将解析后的内容格式化为适合AI处理的文本
    
    Args:
        content: 解析后的文档内容
        
    Returns:
        格式化后的文本
    """
    output = []
    
    if content["title"]:
        output.append(f"# {content['title']}")
        output.append("")
    
    # 添加段落
    if content["paragraphs"]:
        output.append("## 文档内容")
        for para in content["paragraphs"]:
            output.append(para)
            output.append("")
    
    # 添加章节
    if content["sections"]:
        output.append("## 章节结构")
        for section in content["sections"]:
            level = "#" * (section["level"] + 1)
            output.append(f"{level} {section['title']}")
            for line in section["content"]:
                output.append(line)
            output.append("")
    
    # 添加表格
    if content["tables"]:
        output.append("## 表格数据")
        for i, table in enumerate(content["tables"], 1):
            output.append(f"### 表格 {i}")
            for row in table:
                output.append("| " + " | ".join(row) + " |")
            output.append("")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='解析需求文档')
    parser.add_argument('files', nargs='+', help='要解析的文档路径')
    parser.add_argument('--output', '-o', help='输出JSON文件路径')
    parser.add_argument('--format', choices=['json', 'text', 'markdown'], 
                       default='markdown', help='输出格式')
    
    args = parser.parse_args()
    
    results = {}
    for file_path in args.files:
        try:
            print(f"正在解析: {file_path}")
            content = parse_document(file_path)
            results[file_path] = {
                "status": "success",
                "content": content
            }
            print(f"✓ 解析成功: {file_path}")
        except Exception as e:
            results[file_path] = {
                "status": "error",
                "error": str(e)
            }
            print(f"✗ 解析失败: {file_path} - {e}")
    
    # 输出结果
    if args.format == 'json':
        output = json.dumps(results, ensure_ascii=False, indent=2)
    else:
        output_parts = []
        for file_path, result in results.items():
            output_parts.append(f"\n{'='*60}")
            output_parts.append(f"文件: {file_path}")
            output_parts.append(f"{'='*60}")
            
            if result["status"] == "success":
                if args.format == 'markdown':
                    output_parts.append(format_content_for_ai(result["content"]))
                else:
                    # 纯文本格式
                    content = result["content"]
                    if content["title"]:
                        output_parts.append(f"标题: {content['title']}")
                    for para in content["paragraphs"]:
                        output_parts.append(para)
                    for section in content["sections"]:
                        output_parts.append(f"\n{section['title']}")
                        for line in section["content"]:
                            output_parts.append(line)
            else:
                output_parts.append(f"错误: {result['error']}")
        
        output = "\n".join(output_parts)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\n结果已保存到: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
