# Skill 分类参考

分类不是单一维度。创建 Skill 时，建议按下面三个维度依次确认。

## 1. 功能领域（用于标签、检索、目录）

| 领域         | 说明                            | 示例                                 |
| ------------ | ------------------------------- | ------------------------------------ |
| code         | 代码审查、生成、重构、规范      | code-reviewer, java-coding-standards |
| doc          | 文档生成、PDF、Word、Markdown   | docx, pdf                            |
| data         | 数据处理、CSV、JSON、转换、分析 | csv-analysis                         |
| design       | UI/UX、视觉、品牌、CSS          | frontend-design                      |
| research     | 调研、竞品分析、文献综述        | deep-research                        |
| search       | 网页搜索、信息查找              | search                               |
| devops       | 部署、CI/CD、基础设施           | k8s-manifest-generator               |
| testing      | QA、UI 测试、测试生成           | ui-test                              |
| ai           | Agent 工程、评估、MCP、提示安全 | agent-evaluation                     |
| business     | 商业、运营、法律、金融          | SWOT, contract-review                |
| productivity | 办公效率、流程自动化            | meeting-notes                        |
| integration  | 外部工具/API 包装               | github, slack                        |
| meta         | 关于 Skill / Agent 的 Skill     | create-skill                         |
| other        | 以上未覆盖                      | -                                    |

## 2. 知识封装形式（决定目录结构）

| 形式                 | 说明                     | 推荐结构                                |
| -------------------- | ------------------------ | --------------------------------------- |
| text-backed / 指引型 | 原则、指南、清单、方法论 | `SKILL.md` + `references/`              |
| code-backed / 执行型 | 确定性操作、脚本、API    | `SKILL.md` + `scripts/`                 |
| hybrid / 混合型      | 既有指导又有脚本         | `SKILL.md` + `scripts/` + `references/` |

## 3. 产出形态（决定验证指标）

| 类型        | 产出       | 核心指标           |
| ----------- | ---------- | ------------------ |
| knowledge   | 资料、答案 | 命中率、信息密度   |
| SOP         | 执行动作   | 成功率、步骤遵循度 |
| methodology | 思考框架   | 思维引导有效性     |

## 4. 设计模式（可选）

| 模式                | 说明                           |
| ------------------- | ------------------------------ |
| Wrapper             | 包装外部工具或 API             |
| Workflow            | 引导多步流程                   |
| Reference           | 提供知识/上下文                |
| Router / Index-like | 先索引，后加载，对应渐进式披露 |
| Guideline-like      | 提供判断准则，而不是固定流程   |