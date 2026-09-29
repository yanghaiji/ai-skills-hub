---
name: test-case-generator
description: "从需求文档自动生成测试用例、Python自动化测试代码、Excel测试用例、XMind思维导图和测试报告。支持docx/pdf/md/txt/png/jpg格式的需求文档，支持Git仓库分支集成。触发条件：生成测试用例、创建测试、自动化测试、测试报告、需求转测试、test case generation、思维导图、xmind。"
metadata:
  author: Yanghaiji
  version: "5.6.0"
---

# Test Case Generator v5.6

从需求文档自动生成完整的测试解决方案，支持 Git 仓库集成。

## 核心特性

- **统一Python测试**：无论项目是什么语言，都用Python pytest生成测试代码
- **多格式输出**：支持JSON、Excel、XMind思维导图、HTML报告
- **多格式文档支持**：支持 .docx、.pdf、.md、.txt、.png、.jpg 格式的需求文档
- **图片型PDF支持**：自动识别并OCR识别图片型PDF（需安装Tesseract OCR）
- **Git仓库集成**：支持克隆仓库、切换分支/commit
- **交互式选择**：运行时可选择要生成的内容
- **一键运行**：通过main.py实现完整流程自动化

## 工作流程

> **核心原则**：需求文档是必须的；只有当用户选择生成「Python测试代码」或「测试报告」时，才需要额外提供代码仓库地址。

**Step 1: 收集需求文档**

向用户询问需求文档路径。如果用户在触发时已附带文档路径，可直接使用。

使用 `question` 工具询问：

```json
{
  "questions": [{
    "question": "请提供需求文档的路径（支持 .docx / .pdf / .md / .txt / .png / .jpg）:",
    "header": "需求文档",
    "options": [
      {"label": "手动输入路径", "description": "请在 Other 中输入需求文档的完整路径"}
    ]
  }]
}
```

**Step 2: 询问生成内容**

使用 `question` 工具询问用户需要生成哪些内容：

```json
{
  "questions": [{
    "question": "请选择要生成的内容（可多选）:",
    "header": "生成内容选择",
    "options": [
      {"label": "JSON测试用例", "description": "生成 test_cases.json 结构化文件"},
      {"label": "Excel测试用例", "description": "生成 test_cases.xlsx 文件，带颜色格式"},
      {"label": "XMind思维导图", "description": "生成 test_cases.xmind 思维导图"},
      {"label": "Python测试代码", "description": "生成 pytest 测试代码（需要提供代码仓库）"},
      {"label": "测试报告", "description": "运行测试并生成 HTML 报告（需要提供代码仓库）"},
      {"label": "全部生成", "description": "生成所有内容（需要提供代码仓库）"}
    ],
    "multiSelect": true
  }]
}
```

**Step 2.1: 条件追问 — 代码仓库信息**

如果用户在 Step 2 中选择了「Python测试代码」「测试报告」或「全部生成」，**必须追加询问**代码仓库信息：

```json
{
  "questions": [{
    "question": "生成测试代码需要代码仓库，请提供仓库地址:",
    "header": "代码仓库",
    "options": [
      {"label": "手动输入仓库地址", "description": "请在 Other 中输入 Git 仓库 URL"}
    ]
  }]
}
```

获取仓库地址后，继续询问分支（可选）：

```json
{
  "questions": [{
    "question": "请提供分支名称（可选，不填则使用默认分支）:",
    "header": "分支名称",
    "options": [
      {"label": "使用默认分支", "description": "使用仓库的默认分支（main/master）"},
      {"label": "指定分支", "description": "请在 Other 中输入分支名称"}
    ]
  }]
}
```

> **注意**：如果用户只选择了 JSON/Excel/XMind 测试用例（不涉及测试代码和测试报告），则**不需要**询问仓库信息。

**Step 3: 执行生成**

根据用户选择和收集的信息，使用相应的命令行参数执行：

```bash
# 场景A: 只生成测试用例（不需要仓库）
python <skill_dir>/main.py --doc <文档路径> --no-code --skip-tests

# 场景B: 生成测试代码（需要仓库）
python <skill_dir>/main.py --doc <文档路径> --repo <仓库地址> --branch <分支名> --no-excel --no-xmind

# 场景C: 全部生成（需要仓库）
python <skill_dir>/main.py --doc <文档路径> --repo <仓库地址> --branch <分支名>
```

**Step 4: 输出生成结果**

告知用户生成了哪些文件及文件位置。

## 代码读取范围限制

> **重要**：分析代码时，只读取与需求文档内容相关的代码模块，**禁止全量扫描整个仓库**。

具体规则：
1. 先解析需求文档，提取关键业务模块和接口名称
2. 在仓库中只定位与需求相关的目录和文件（如需求提到「用户登录」，只读取 auth/login 相关代码）
3. 使用 `--repo` 克隆仓库后，通过目录结构筛选相关模块，不要对所有文件做代码分析
4. 生成的测试代码只覆盖需求文档中描述的功能点，不额外扩展

## 测试用例生成规范

> **核心原则**：测试用例必须基于需求文档的业务语义，使用专业测试语言，禁止模板化生成。

### 命名规范

- **测试用例名称**：使用「场景 + 动作 + 预期」格式，体现具体业务场景
  - ✅ `用户输入正确手机号和验证码后成功登录`
  - ✅ `订单金额超过库存上限时提交失败并提示库存不足`
  - ❌ `处理数据功能测试`
  - ❌ `验证Service方法是否正常工作`

- **测试描述**：一句话说明测试目的，包含前置条件和验证点
  - ✅ `验证用户在未登录状态下访问订单页面时，系统自动跳转到登录页`
  - ❌ `验证xxx方法是否正常工作`

### 测试步骤规范

步骤必须具体、可执行，包含真实业务数据：
- ✅ `1. 打开登录页面，输入手机号 13800138000`
- ✅ `2. 输入短信验证码 123456`
- ✅ `3. 点击「登录」按钮`
-  `1. 调用xxxService.xxx方法`
- ❌ `2. 验证返回结果`

### 预期结果规范

预期结果必须明确、可验证：
- ✅ `页面跳转到首页，右上角显示用户昵称「张三」`
- ✅ `返回 HTTP 400，响应体包含 {"code": 400, "msg": "库存不足"}`
- ❌ `返回预期结果`
- ❌ `系统保持稳定`

### 测试类型覆盖

每个功能点至少覆盖以下维度：
1. **正常流程**：主流程 happy path
2. **边界条件**：空值、最大值、最小值、特殊字符
3. **异常场景**：网络超时、权限不足、数据冲突
4. **业务规则**：状态机流转、权限控制、数据一致性

### 生成方式

**由 Agent 直接基于需求文档内容生成**，不使用模板匹配。Agent 应：
1. 理解需求文档中的业务流程和功能点
2. 结合测试专业知识，设计覆盖全面的测试场景
3. 使用真实业务术语和具体数据
4. 按优先级排列（核心功能 > 边界条件 > 异常场景）

## XMind 生成规范

> **核心原则**：XMind 是测试思路的全景视图，展示测试策略和关键链路，不是测试用例的平铺列表。

### 结构设计

XMind 采用**三层结构**：

```
[项目名称] 测试策略
├──  测试概览
│   ├── 测试范围
│   ├── 测试策略
│   └── 风险评估
├── 🔑 关键业务链路（核心）
│   ├── 链路1: [业务场景名称]
│   │   ├── 正常流程
│   │   ├── 异常分支
│   │   └── 边界条件
│   └── 链路2: [业务场景名称]
│       └── ...
├── 📦 功能模块测试
│   ├── 模块A
│   │   ├── 功能点1（含关键测试点）
│   │   └── 功能点2
│   └── 模块B
└── ️ 专项测试
    ├── 性能测试点
    ├── 安全测试点
    └── 兼容性测试点
```

### 各层说明

1. **测试概览**：整体测试方向、范围、策略说明
2. **关键业务链路**：端到端的核心业务流程，标注正常/异常/分支路径
3. **功能模块测试**：按模块拆分的功能测试点，每个功能点列出关键验证项
4. **专项测试**：性能、安全、兼容性等非功能性测试的关注点

### 节点内容要求

- 每个节点用**简短短语**描述测试关注点，不要写完整用例
- 关键链路节点标注**优先级标记**（高/🟡中/🟢低）
- 异常分支用「⚠️」前缀标识
- 不展开具体步骤和预期结果（这些在 Excel/JSON 中）

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--doc, -d` | 需求文档路径（必须） |
| `--repo, -r` | Git仓库地址（生成测试代码时必须） |
| `--branch, -b` | 分支名（可选，默认使用默认分支） |
| `--commit, -c` | Commit hash（可选） |
| `--output, -o` | 输出目录（默认 ./test_output） |
| `--no-excel` | 不生成Excel |
| `--no-xmind` | 不生成XMind |
| `--no-code` | 不生成Python测试代码 |
| `--skip-tests` | 跳过测试运行 |
| `--only-json` | 只生成JSON |
| `--only-excel` | 只生成Excel |
| `--only-xmind` | 只生成XMind |

## 输出文件

| 文件 | 说明 |
|------|------|
| `test_cases.json` | JSON格式测试用例 |
| `test_cases.xlsx` | Excel测试用例（带颜色） |
| `test_cases.xmind` | XMind测试策略思维导图（概览+关键链路+功能模块+专项测试） |
| `generated_tests/` | Python pytest测试代码 |
| `test_report.html` | HTML测试报告 |

## 生成的测试代码

无论项目是什么语言，都生成**Python pytest**测试代码：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""自动生成的统一测试代码"""

import pytest
import requests
from unittest.mock import Mock, patch

# 配置
BASE_URL = "http://localhost:8080"

# Fixtures
@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

# 工具函数
def assert_response_success(response, expected_status=200):
    assert response.status_code == expected_status
    return response.json()

# 测试类
class TestUserLogin:
    def test_login_success(self, api_client):
        """测试登录成功"""
        # Arrange
        login_data = {"username": "test", "password": "123456"}
        
        # Act
        response = api_client.post(f"{BASE_URL}/auth/login", json=login_data)
        
        # Assert
        data = assert_response_success(response)
        assert "token" in data
```

## 使用场景

### 场景1: 只生成测试用例文档（不需要代码仓库）
```
用户提供：需求文档 requirements.docx
选择：JSON + Excel + XMind
→ python main.py --doc requirements.docx --no-code --skip-tests
```

### 场景2: 生成测试代码（需要代码仓库）
```
用户提供：需求文档 requirements.docx + 仓库 https://github.com/user/project.git + 分支 main
选择：Python测试代码 + 测试报告
→ python main.py --doc requirements.docx --repo https://github.com/user/project.git --branch main --no-excel --no-xmind
```

### 场景3: 全部生成（需要代码仓库）
```
用户提供：需求文档 api_spec.md + 仓库 https://github.com/user/project.git + 分支 develop
选择：全部生成
→ python main.py --doc api_spec.md --repo https://github.com/user/project.git --branch develop
```

## 依赖安装

首次使用会自动安装以下Python包：

```bash
pip install python-docx pdfplumber pytest pytest-html openpyxl requests
```

## 注意事项

1. **需求文档必须**：整个流程必须提供需求文档作为输入
2. **仓库按需提供**：只有生成测试代码/测试报告时才需要代码仓库
3. **修改BASE_URL**：生成后需要根据实际项目修改 `BASE_URL`
4. **修改API路径**：需要根据实际API修改测试方法中的端点路径
5. **添加Mock**：外部依赖需要添加Mock对象
6. **Git访问权限**：确保有仓库的读取权限

## 故障排除

### 文档解析失败
- 检查文件格式是否支持
- 确认文件未损坏

### Git克隆失败
- 检查仓库地址是否正确
- 确认有仓库的读取权限

### 测试运行失败
- 检查pytest是否安装
- 确认BASE_URL配置正确

## 参考资料

- `references/test_patterns.md` - 测试模式参考
- `references/best_practices.md` - 测试最佳实践
- `references/examples.md` - 测试用例示例

---

*无论项目是什么语言，都统一用Python pytest生成测试代码。*
