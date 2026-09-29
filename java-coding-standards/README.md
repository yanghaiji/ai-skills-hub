# Java 开发规范 Skill

基于《阿里巴巴 Java 开发手册（黄山版）》的完整 Java 开发规范。

## 目录结构

```
java-coding-standards/
├── SKILL.md                          # 核心规范文档（~300行，每次加载）
├── README.md                         # 本文件
└── references/                       # 按需加载的参考文档
    ├── detailed-examples.md          # 各章节完整代码示例与补充规约
    ├── extended-rules.md             # 控制语句、注释、安全、SQL、测试、项目结构
    └── templates.md                  # 标准 Controller/Service/DTO/异常处理模板
```

### 加载策略

| 文件 | 加载时机 | 内容概要 |
|------|----------|----------|
| `SKILL.md` | 每次编写 Java 代码时 | 核心规约要点（命名、OOP、集合、异常、并发等 13 章） |
| `references/detailed-examples.md` | 需要详细代码示例时 | 完整 PASS/FAIL 示例、集合陷阱、NPE 场景、并发锁规范 |
| `references/extended-rules.md` | 涉及控制语句/注释/安全/SQL 时 | 控制语句、注释规约、安全规约、测试期望、项目结构 |
| `references/templates.md` | 创建新类/模块时 | 标准 Controller / Service / DTO / 异常处理模板 |

## 核心规范模块

| 模块 | 描述 |
|------|------|
| 命名规范 | 变量、方法、类、常量命名规则 |
| 代码格式 | 缩进、空格、注释格式 |
| OOP 规约 | 面向对象编程最佳实践 |
| 集合处理 | 集合使用与优化 |
| 并发处理 | 线程安全与并发编程 |
| 异常处理 | 异常捕获与使用规范 |
| 日志规范 | 日志输出与级别管理 |
| 安全规约 | 安全编码与数据保护 |

## 使用方式

### 1. 作为 AI 提示词
在让 AI 编写 Java 代码时，附上规范说明：
```
请按照阿里巴巴 Java 开发规范编写以下代码：[需求描述]
```

### 2. 作为代码审查清单
代码审查时逐项检查：
- 命名规范
- 异常处理
- 日志输出
- 安全编码

### 3. 结合 IDE 插件
- **IDEA**: Alibaba Java Coding Guidelines
- **SpotBugs**: 静态代码分析
- **PMD**: 代码规范检查

## 关键速查

### 命名速查
```
类名: UpperCamelCase     → UserDO, HtmlDTO
方法: lowerCamelCase     → getUserInfo()
常量: UPPER_SNAKE_CASE   → MAX_STOCK_COUNT
包名: lowercase          → com.example.service
```

### 集合初始化
```java
// 推荐：预估容量
new ArrayList<>(16);
new HashMap<>(16);

// 禁止：无参构造
new ArrayList<>();
new HashMap<>();
```

### 日志输出
```java
// 推荐：占位符
logger.info("用户登录成功, userId={}", userId);

// 禁止：字符串拼接
logger.info("用户登录成功: " + userId);
```

## 版本信息

- 基于：阿里巴巴 Java 开发手册（黄山版）
- 创建：2026-09-04
- 更新：2026-09-07（v1.2 精简为 300 行核心 + references 按需加载）
