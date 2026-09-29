# Requirement to Code

从需求文档自动生成符合项目风格的代码，支持 Git 仓库集成。

## 功能特性

- **多格式文档支持**: 支持 .pdf、.md、.txt、.docx、.doc、.ppt、.pptx 格式的需求文档
- **代码风格分析**: 自动分析项目代码风格（命名规范、缩进、注释风格等）
- **Git仓库集成**: 支持克隆仓库、切换分支/commit，在指定分支上开发
- **智能代码生成**: 基于需求和现有代码风格生成符合规范的代码
- **增量开发**: 只修改/新增与需求相关的代码，不破坏现有功能

## 安装

首次使用会自动安装依赖，也可以手动安装：

```bash
pip install pdfplumber python-docx python-pptx
```

## 使用方法

### 命令行使用

```bash
# 只分析代码风格
python main.py --analyze-only --repo /path/to/repo

# 从需求文档生成代码（本地仓库）
python main.py --doc requirements.md --repo /path/to/repo --branch feature/login

# 从需求文档生成代码（Git仓库）
python main.py --doc requirements.pdf --repo https://github.com/user/project.git --branch develop

# 指定输出目录
python main.py --doc requirements.md --repo /path/to/repo -o ./my_output
```

### 在 opencode 中使用

当用户提出以下需求时，会自动触发此 skill：

- 需求开发
- 根据需求写代码
- requirement to code
- 需求转代码
- 自动开发

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--doc, -d` | 需求文档路径（支持 .pdf, .md, .txt, .docx, .doc, .ppt, .pptx） |
| `--repo, -r` | 代码仓库位置（本地路径或Git URL） |
| `--branch, -b` | 分支名（可选，默认使用默认分支） |
| `--output, -o` | 输出目录（默认 ./code_output） |
| `--analyze-only` | 只分析代码风格，不生成代码 |
| `--dry-run` | 模拟运行，显示将要修改的文件但不实际修改 |

## 工作流程

1. **收集需求文档**: 读取并解析需求文档
2. **分析代码风格**: 分析项目的代码风格、命名规范、结构模式
3. **提取功能点**: 从需求中提取需要实现的功能
4. **生成代码**: 根据需求和代码风格生成代码
5. **输出结果**: 生成代码文件和变更摘要

## 输出文件

| 文件 | 说明 |
|------|------|
| `code_analysis.json` | 代码风格分析结果 |
| `generated_code/` | 生成的代码文件 |
| `changes_summary.md` | 修改摘要 |

## 示例

### 场景1: 本地仓库开发

```bash
python main.py --doc requirements.md --repo E:\projects\my-app --branch feature/login
```

### 场景2: Git仓库开发

```bash
python main.py --doc api_spec.pdf --repo https://github.com/user/project.git --branch develop
```

### 场景3: 只分析代码风格

```bash
python main.py --analyze-only --repo E:\projects\my-app
```

## 支持的编程语言

- Python
- JavaScript/TypeScript
- Java
- Go
- 其他语言（生成需求分析文档）

## 注意事项

1. 需求文档和代码仓库都是必须的
2. 分支不存在会自动创建
3. 建议在开发前备份代码或使用Git版本控制
4. 生成的代码需要人工审查确认

## 目录结构

```
requirement-to-code/
├── SKILL.md              # Skill配置文件
├── main.py               # 主入口脚本
├── README.md             # 说明文档
├── scripts/
│   ├── parse_document.py # 文档解析模块
│   ├── git_handler.py    # Git操作处理
│   ├── code_analyzer.py  # 代码风格分析
│   └── code_generator.py # 代码生成
└── references/
    └── code_styles.md    # 代码风格参考
```
