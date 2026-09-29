---
name: pdf-reader
description: 从PDF文件中提取文本和表格。使用场景：用户要求读取、解析、提取PDF内容，或加载PDF开发规范时触发。支持自动发现默认目录下的PDF文件。
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# PDF Reader

通过 Python 脚本从 PDF 文件中提取文本和表格内容。

## 依赖安装

仅需安装一次：

```bash
pip install pdfplumber
```

## Skill 脚本路径

所有脚本位于本 Skill 目录下的 `scripts/` 子目录。

> `<skill_dir>` 代表本 SKILL.md 所在目录的绝对路径，调用时替换为实际路径。

## 脚本一览

| 脚本 | 用途 | 适用场景 |
|------|------|----------|
| `extract_all.py` | 一次提取文本 + 表格 | **默认首选**，全量提取 |
| `extract_text.py` | 仅提取文本 | 只需文字内容时 |
| `extract_tables.py` | 仅提取表格 | 只需表格数据时 |

## 使用方式

### 全量提取（推荐）

```bash
python <skill_dir>/scripts/extract_all.py <pdf_path> [--pages 1,2,3] [--output result.txt]
```

- `--pages`：指定页码（1-based），不填则提取全部页面
- `--output / -o`：将结果保存到文件（大文件时推荐）

### 仅提取文本

```bash
python <skill_dir>/scripts/extract_text.py <pdf_path> [--pages 1,2,3]
```

### 仅提取表格

```bash
python <skill_dir>/scripts/extract_tables.py <pdf_path> [--pages 1,2,3] [--format markdown|csv]
```

## 自动发现 PDF

当用户未指定具体 PDF 路径时，按以下顺序自动扫描：

1. **项目目录**：项目根目录下的 `docs/`、`doc/`、`specs/` 子目录
2. **Skill 文档目录**：`<skill_dir>/docs/`
3. **当前工作目录**：用户当前打开的文件所在目录

扫描时查找所有 `.pdf` 文件，如果有多个则列出供用户选择。

## 工作流程

1. **确定任务**：用户需要文本、表格、还是全部？
2. **检查依赖**：确保 `pdfplumber` 已安装
3. **定位 PDF**：使用用户指定路径，或自动发现
4. **执行提取**：运行对应脚本，**注意用引号包裹含特殊字符的路径**
5. **处理结果**：基于提取内容完成用户请求

## 注意事项

- **扫描件/图片 PDF** 无法提取文字（pdfplumber 仅支持文字型 PDF），遇到时提醒用户
- **大型 PDF**（>20页）：使用 `--pages` 分批提取，或使用 `--output` 保存到文件后再读取
- **路径含特殊字符**（括号、空格、中文）：必须用引号包裹路径
- **表格未检测到**：可能是非标准表格结构，改用文本提取作为兜底
