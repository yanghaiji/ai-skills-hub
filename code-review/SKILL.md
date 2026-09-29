---
name: code-review
description: "Code Review 全流程指南：从变更分析到结构化审查报告。覆盖正确性、安全性、性能、可维护性、规范性五大维度。触发条件：代码审查、PR Review、让AI审查代码时。支持与 java-coding-standards、security-coding、sql-standards 等 Skill 联动。"
metadata:
  author: Yanghaiji
  version: "2.0.0"
---

# Code Review 审查指南

结构化的代码审查工作流，帮助 Agent 系统性地发现问题并输出专业审查报告。

## 何时激活

* 用户要求审查代码、Review 代码、PR Review 时
* 用户提交代码变更要求检查时
* **每次让 AI 审查代码时必须触发此规范**

---

## 一、审查工作流

每次 Code Review 必须按以下流程执行，不可跳过步骤。

### 步骤 1：获取变更上下文

1. 确认审查范围（文件列表、diff、分支对比）
2. 识别变更类型：新功能 / Bug 修复 / 重构 / 配置变更
3. 识别涉及的技术栈和语言（Java / TypeScript / Python / SQL 等）
4. 如变更涉及特定领域，**加载对应 Skill**（见「联动 Skill」章节）

### 步骤 2：快速浏览（全局理解）

1. 阅读 PR/MR 描述，理解变更意图
2. 浏览变更的文件结构，理解影响范围
3. 识别核心变更文件 vs 辅助变更文件（测试、配置、文档）
4. 初步判断变更规模：小型（<5 文件）/ 中型（5-15 文件）/ 大型（>15 文件）

### 步骤 3：逐文件深度审查

按优先级审查，每个文件依次检查五大维度（见下文「审查维度」）：

1. **核心业务逻辑文件**（Service / UseCase / Handler）
2. **数据层文件**（Repository / DAO / Model）
3. **接口层文件**（Controller / API / DTO）
4. **配置与基础设施文件**
5. **测试文件**

### 步骤 4：整体评估

1. 跨文件的架构一致性
2. 变更是否引入破坏性改动
3. 是否遗漏必要的变更（如改了接口但没改文档）

### 步骤 5：输出审查报告

按「输出格式」章节的模板生成结构化报告。

---

## 二、严重等级定义

每个发现的问题必须标注严重等级：

| 等级 | 标识 | 含义 | 要求 |
|------|------|------|------|
| **Blocker** | 🔴 | 必须修复才能合并：Bug、安全漏洞、数据丢失风险 | 修复后重新审查 |
| **Major** | 🟠 | 强烈建议修复：性能问题、并发隐患、错误处理缺失 | 修复后确认 |
| **Minor** | 🟡 | 建议修复：命名不规范、缺少注释、代码风格问题 | 本次或下次修复 |
| **Suggestion** | 💡 | 优化建议：更好的实现方式、设计改进 | 可选采纳 |

---

## 三、审查维度

### 3.1 正确性

- 逻辑是否正确，边界条件是否处理
- 空值/异常路径是否处理，并发场景是否安全
- 是否符合需求描述，业务规则是否正确实现
- 数据一致性是否保证（事务、幂等、并发写入）

```java
// ❌ 边界条件未处理
public int divide(int a, int b) {
    return a / b;  // b=0 时异常
}

// ✅ 处理边界
public int divide(int a, int b) {
    if (b == 0) {
        throw new IllegalArgumentException("除数不能为0");
    }
    return a / b;
}
```

### 3.2 安全性

- 外部输入是否校验（类型、长度、范围、格式）
- SQL 注入 / XSS / CSRF 防护
- 敏感数据是否加密存储、日志是否脱敏
- 接口权限校验、数据越权风险
- 硬编码密钥/密码/Token

```java
// ❌ 日志泄露敏感信息
log.info("用户登录: {}", user);

// ✅ 日志脱敏
log.info("用户登录: {}", user.withMaskedPhone());
```

### 3.3 性能

- 数据库：索引是否命中、N+1 问题、批量操作是否分批
- 缓存：热点数据是否缓存、缓存穿透/击穿防护
- 资源：连接是否释放、流是否关闭、内存泄漏
- 算法：时间/空间复杂度是否合理

```java
// ❌ N+1 问题
List<Order> orders = orderRepository.findAll();
for (Order order : orders) {
    User user = userRepository.findById(order.getUserId()); // 循环查询
}

// ✅ 批量查询
Set<Long> userIds = orders.stream().map(Order::getUserId).collect(toSet());
Map<Long, User> userMap = userRepository.findByIdIn(userIds);
```

### 3.4 可维护性

- 命名是否见名知意，函数职责是否单一
- 函数长度（< 50 行）、参数数量（< 5 个）
- 是否遵循 SOLID 原则，重复代码是否提取
- 魔法数字是否提取为常量
- 测试是否覆盖核心路径

### 3.5 规范性

- 编码规范（命名、格式、注释）
- Git 规范（提交信息、分支命名、变更范围）
- 项目特定规范（如有 PDF 规范或 `.ai/specs/` 目录）

---

## 四、联动 Skill

审查时根据代码语言和内容，**自动加载对应 Skill** 作为审查依据：

| 审查场景 | 必须加载的 Skill | 触发条件 |
|----------|-----------------|----------|
| Java / Spring Boot 代码 | `java-coding-standards` | 检测到 `.java` 文件 |
| 安全相关代码（认证、加密、输入处理） | `security-coding` | 涉及 auth/crypto/input |
| SQL 语句或 ORM 查询 | `sql-standards` | 检测到 SQL / HQL / JPQL |
| React / TypeScript 前端代码 | `react-typescript-standards` | 检测到 `.tsx` / `.ts` 文件 |
| Python 代码 | `python-standards` | 检测到 `.py` 文件 |
| Redis 相关操作 | `redis-standards` | 涉及 Redis 客户端调用 |
| Docker 配置 | `docker-standards` | 检测到 Dockerfile |
| 接口 API 设计 | `api-design` | 涉及 REST API 定义 |

**加载方式**：读取对应 Skill 的 SKILL.md 文件，以其规范作为审查标准，发现的问题在报告中标注来源。

---

## 五、审查报告输出格式

每份审查报告必须包含以下结构：

### 5.1 报告头部

```markdown
## 📋 Code Review 报告

- **审查范围**：[文件数量] 个文件，[变更行数] 行变更
- **变更类型**：[新功能/Bug修复/重构/配置]
- **审查时间**：[日期]
- **总体评价**：[通过/需修改后通过/需重大修改]
```

### 5.2 问题汇总

```markdown
### 📊 问题统计
| 等级 | 数量 |
|------|------|
| 🔴 Blocker | N |
| 🟠 Major | N |
| 🟡 Minor | N |
| 💡 Suggestion | N |
```

### 5.3 问题详情

每个问题按以下格式输出：

```markdown
#### [等级] 问题标题

- **文件**：`path/to/file.java` L42-L48
- **维度**：[正确性/安全性/性能/可维护性/规范性]
- **依据**：[引用具体规范条目，如 java-coding-standards 九、异常处理]

**问题描述**：
简要说明问题是什么、为什么是问题。

**建议修改**：
```java
// 修改后的代码
```

**严重程度说明**（仅 Blocker/Major）：
解释可能造成的影响。
```

### 5.4 亮点（可选）

如果代码中有值得肯定的设计，列出以鼓励良好实践。

### 5.5 总结

```markdown
### 📝 总结

[1-3 句话概括审查结论，列出最关键的改进方向]
```

---

## 六、审查原则

1. **对事不对人** — 评论代码，不评论人
2. **解释原因** — 每个建议都要说明"为什么"
3. **区分必须改和建议改** — 用严重等级明确区分
4. **给出修改建议** — 不只指出问题，要给出具体修改方案
5. **关注风险** — 优先关注 Blocker/Major，不要纠结细枝末节
6. **考虑上下文** — 结合业务场景判断，不生搬硬套规则

---

## 七、`references/` 按需加载指令

以下文件**不会自动加载**，Agent 必须根据当前审查场景**主动读取**对应文件：

| 触发场景 | 必须读取的文件 |
|----------|---------------|
| 需要完整的逐条检查清单（Checklist） | `references/detailed-checklist.md` |
| 需要审查报告的完整输出模板和示例 | `references/output-format.md` |

**常规审查**：仅使用本文件（SKILL.md）即可覆盖大部分场景。

**深度审查**（大型变更、安全敏感模块、核心业务逻辑）：加载 `detailed-checklist.md` 获取逐条检查项。

*基于：Google Engineering Practices + GitHub Code Review Best Practices*
