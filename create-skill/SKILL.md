---
name: create-skill
description: "Create new skills through an interactive guided workflow. Use when the user wants to create a new skill, build a skill from scratch, set up a skill project, or needs help structuring a skill. Do not use when the user is only asking about skill concepts, editing an existing skill, or debugging a skill. Triggers: 'create skill', 'new skill', 'build skill', 'make a skill', 'skill template', 'skill wizard', '创建 skill', '新建 skill'."
compatibility: "Requires Bash for script execution. Windows users may need Git Bash or WSL for chmod commands."
license: MIT
allowed-tools: AskUserQuestion, Read, Write, Bash, Glob
metadata:
  author: Yanghaiji
  version: "2.0.0"
argument-hint: "[skill-name]"
---

# 创建 Skill

交互式向导：帮助用户创建结构规范、分类清晰、可验证的 Skill。

## 何时使用

- 用户想从零创建新 Skill。
- 用户需要 Skill 模板、目录结构或 frontmatter 建议。
- 用户说“创建 skill / 新建 skill / skill wizard”。

## 何时不使用

- 用户只是询问 Skill 概念、分类或最佳实践。
- 用户要编辑、调试、删除已有 Skill。
- 用户要创建普通 Prompt，而不是可复用 Skill。

## 工作流程

### Step 1: 分类

使用 `AskUserQuestion` 依次确认三个维度。分类表见 `references/classification.md`。

**1a. 功能领域**（单选，用于标签与检索）

`code`、`doc`、`data`、`design`、`research`、`search`、`devops`、`testing`、`ai`、`business`、`productivity`、`integration`、`meta`、`other`

**1b. 知识封装形式**（单选，决定目录结构）

| 选项 | 说明 | 生成结构 |
| --- | --- | --- |
| `text-backed` / 指引型 | 原则、指南、清单、方法论 | `SKILL.md` + `references/` |
| `code-backed` / 执行型 | 确定性操作、脚本、API | `SKILL.md` + `scripts/` |
| `hybrid` / 混合型 | 既有指导又有脚本 | `SKILL.md` + `scripts/` + `references/` |

**1c. 产出形态**（单选，决定验证重点）

| 选项 | 产出 | 验证重点 |
| --- | --- | --- |
| `knowledge` | 资料、答案 | 命中率、信息密度 |
| `SOP` | 执行动作 | 成功率、步骤遵循度 |
| `methodology` | 思考框架 | 思维引导有效性 |

### Step 2: 收集细节

**必问：**

1. Skill 名称（kebab-case）
2. 一句话描述（会出现在 `available_skills`）
3. 触发短语（逗号分隔，中英文均可）

**选问：**

4. 是否需要 `assets/`？类型？（HTML 模板、配置模板、脚手架等）
5. 允许使用的工具？默认：`Read, Write, Bash, AskUserQuestion`
6. License？默认 MIT

**根据 1b 自动决定，不再询问：**

- `text-backed` → 生成 `references/`，跳过脚本问题
- `code-backed` → 生成 `scripts/`，跳过 references 问题
- `hybrid` → 两者都生成

### Step 3: 生成目录

**默认在当前工作目录下创建：**

```text
./{skill-name}/
├── SKILL.md          # 必须
├── scripts/          # code-backed / hybrid
├── references/       # text-backed / hybrid
└── assets/           # 可选
    └── templates/
```

如果用户希望放在其他位置，直接使用用户指定的路径。  
若目标目录已存在，询问：覆盖 / 重命名 / 取消。

### Step 4: 生成 SKILL.md

使用 `references/templates.md` 中的模板。必须满足：

- frontmatter 包含 `name`、`description`、`license`、`allowed-tools`。
- `description` 必须包含 `Use when`、`Do not use when` 和 `Triggers:`。
- 正文使用中文；工具名、字段名、kebab-case 保留英文。
- 主文件建议 ≤ 120 行；长内容放 `references/`。

### Step 5: 脚本与资源设置

**脚本（code-backed / hybrid）：**

1. 创建 `scripts/`。
2. 按语言生成 starter script，模板见 `references/templates.md`。
3. 在 `## Setup` 写明依赖与执行方式。
4. 设置脚本权限（跨平台兼容）：
   - **Linux/macOS**: `chmod +x scripts/*`
   - **Windows**: 使用 Git Bash 或 WSL 执行上述命令，或手动设置文件属性

**资源（如需要）：**

1. 创建 `assets/templates/`。
2. 生成占位符模板，示例见 `references/assets-examples.md`。
3. 在 `SKILL.md` 的 `## Usage` 中说明占位符规则和填充方式。

### Step 6: 验证与收尾

创建后运行检查：

- [ ] `name` 为 kebab-case。
- [ ] `description` 含 `Use when`、`Do not use when` 和 `Triggers:`。
- [ ] `allowed-tools` 已声明。
- [ ] 目录结构与 1b 分类一致。
- [ ] 脚本可执行（如适用）。
- [ ] `assets/` 模板仅含占位符，无真实数据。
- [ ] 无时间敏感信息（具体日期、版本号）。
- [ ] 若目录已存在，已按用户选择处理。

**按 1c 选验证重点：**

- `knowledge` → 检查 references 是否完整、索引是否清晰。
- `SOP` → 检查步骤是否可执行、有无分支说明。
- `methodology` → 检查原则/框架是否明确、有无反例。

自动检查（跨平台兼容）：

```bash
# Windows (PowerShell)
Test-Path SKILL.md -PathType Leaf

# Linux/macOS
test -f SKILL.md
```

```bash
# 检查 description 必需字段
grep -q "Use when" SKILL.md && grep -q "Do not use when" SKILL.md && grep -q "Triggers:" SKILL.md && echo "Description fields OK"
```

## 输出位置

**默认写入当前工作目录：**

```text
./{skill-name}/SKILL.md
```

如果用户明确要求放到其他位置，使用用户指定的路径。

## 错误处理

- `AskUserQuestion` 不可用：改为逐条文本提问。
- 用户中断：保存已收集信息到临时文件，并告知如何继续。
- 依赖缺失：提示安装命令，不继续生成可执行脚本。
- 路径无权限：建议换目录，谨慎使用 `sudo`。

## 参考

- `references/classification.md`：三维度分类表
- `references/templates.md`：SKILL.md、脚本、验证模板
- `references/patterns.md`：常见模式（Wrapper、Workflow、Reference、Router）
- `assets/templates/assets-examples.md`：assets 模板示例