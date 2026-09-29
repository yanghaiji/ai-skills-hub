---
name: docx-reader
description: 从Word(.docx)文件中提取文本和表格。使用场景：用户要求读取、解析、提取Word文档内容时触发。支持按段落提取正文、标题、表格，支持自动发现目录下的docx文件。
metadata:
  author: Yanghaiji
  version: "1.0.0"

---

# Docx Reader

通过 Python 脚本从 Word (.docx) 文件中提取文本和表格内容。

## 依赖安装

仅需安装一次：

```bash
pip install python-docx
```

## Skill 脚本路径

所有脚本位于本 Skill 目录下的 `scripts/` 子目录。

> `<skill_dir>` 代表本 SKILL.md 所在目录的绝对路径，调用时替换为实际路径。

## 脚本一览

| 脚本 | 用途 | 适用场景 |
|------|------|----------|
| `extract_all.py` | 一次提取文本 + 表格 | **默认首选**，全量提取 |
| `extract_text.py` | 仅提取文本（按段落） | 只需文字内容时 |
| `extract_tables.py` | 仅提取表格 | 只需表格数据时 |

## 使用方式

### 全量提取（推荐）

```bash
python <skill_dir>/scripts/extract_all.py <docx_path> [--output result.md]
```

- `--output / -o`：将结果保存到文件（大文件时推荐）

### 仅提取文本

```bash
python <skill_dir>/scripts/extract_text.py <docx_path> [--headings-only]
```

- `--headings-only`：仅提取标题段落（Heading 1/2/3 等）

### 仅提取表格

```bash
python <skill_dir>/scripts/extract_tables.py <docx_path> [--format markdown|csv]
```

- `--format`：表格输出格式，默认 `markdown`

## 自动发现 docx

当用户未指定具体路径时，按以下顺序自动扫描：

1. **项目目录**：项目根目录下的 `docs/`、`doc/`、`specs/` 子目录
2. **当前工作目录**：用户当前打开的文件所在目录

扫描时查找所有 `.docx` 文件（排除 `~$` 开头的临时文件），如果有多个则列出供用户选择。

## 工作流程

1. **确定任务**：用户需要文本、表格、还是全部？
2. **检查依赖**：确保 `python-docx` 已安装
3. **定位文件**：使用用户指定路径，或自动发现
4. **执行提取**：运行对应脚本，**注意用引号包裹含特殊字符的路径**
5. **处理结果**：基于提取内容完成用户请求

## 注意事项

- **`.doc` 旧格式不支持**：python-docx 仅支持 `.docx`（Office 2007+），遇到 `.doc` 文件时提醒用户先转换
- **大型文档**（>100页）：使用 `--output` 保存到文件后再读取
- **路径含特殊字符**（括号、空格、中文）：必须用引号包裹路径
- **表格为空**：可能是合并单元格或嵌套表格，脚本会尽力解析但可能丢失部分格式
- **图片/嵌入对象**：脚本不提取图片，仅提取文本和表格
