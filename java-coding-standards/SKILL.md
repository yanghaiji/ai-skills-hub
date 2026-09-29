---
name: java-coding-standards
description: "Spring Boot服务的Java编码标准：命名、常量、OOP、日期时间、集合、并发、异常、控制语句、注释、安全、ORM等规约。触发条件：编写Java代码、创建Spring Boot服务、实现业务逻辑、代码审查、重构代码时。支持通过PDF文件加载项目开发规范。"
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# Java 编码规范

适用于 Spring Boot 服务中可读、可维护的 Java (17+) 代码的编码标准。

## 何时激活

* 在 Spring Boot 项目中编写或审查 Java 代码时
* 强制执行命名、不可变性或异常处理约定时
* 使用记录类、密封类或模式匹配（Java 17+）时
* 审查 Optional、流或泛型的使用时
* **每次让AI编写Java代码时必须触发此规范**

---

## PDF 开发规范加载

当用户指定了 PDF 格式的开发规范文件时，**优先以 PDF 内容为准**。

### 使用方式

用户可通过以下方式指定 PDF 规范：
- "使用 `xxx.pdf` 作为开发规范"
- "按照 `xxx.pdf` 里的规范来写代码"
- "加载 `xxx.pdf` 作为编码标准"
- "按规范写代码"（触发自动发现流程）

### 加载流程

1. **识别 PDF 路径**：从用户指令中提取 PDF 文件的绝对路径或相对路径
2. **自动发现**（用户未指定路径时）：按顺序扫描以下目录中的 `.pdf` 文件：
   - 项目根目录下的 `docs/`、`doc/`、`specs/` 子目录
   - 项目级规范目录 `.ai/specs/`（随代码库提交，Agent 无关）
   - `<pdf-reader-skill-dir>/docs/`（pdf-reader Skill 的文档目录）
   - 如果找到多个 PDF，列出供用户选择
3. **调用 pdf-reader Skill**：使用 `extract_all.py` 脚本提取 PDF 内容
   ```bash
   python '<pdf-reader-skill-dir>/scripts/extract_all.py' '<pdf_path>' --pages <页码>
   ```
4. **智能分页策略**：
   - 总页数 ≤ 20：一次全量提取
   - 总页数 > 20：先提取目录页，识别相关章节，再按需提取对应页面
5. **作为编码依据**：将解析出的规范条目作为当前会话的编码标准，**优先级高于本文件中的默认规范**

### 项目级规范覆盖

项目可在以下位置放置自定义规范文件，实现团队共享：
- `.ai/specs/` — 项目级规范目录（随代码库提交，Agent 无关）
- 支持放置 `.pdf`、`.md` 格式的规范文件

**优先级**：项目级规范 > PDF 规范 > 本 Skill 默认规范

### 注意事项

- PDF 规范**仅在当前会话中生效**，不会修改本 Skill 文件
- `<pdf-reader-skill-dir>` 由 Agent 在运行时解析为 pdf-reader Skill 的实际安装路径
- 路径含括号、空格、中文时，必须用引号包裹

---

## 核心原则

* 清晰优于巧妙
* 默认不可变；最小化共享可变状态
* 快速失败并提供有意义的异常
* 一致的命名和包结构
* 生产级代码：考虑边界、异常、并发、性能

---

## 一、命名规范

- 代码中的命名均不能以下划线或美元符号开始或结束
- 禁止使用拼音与英文混合，禁止使用中文

| 类型 | 风格 | 示例 |
|------|------|------|
| 类名 | UpperCamelCase | `MarketService`、`UserDO`、`HtmlDTO` |
| 方法名/变量 | lowerCamelCase | `findBySlug()`、`marketRepository` |
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE`、`CACHE_KEY_PREFIX` |
| 包名 | 全小写，单数 | `com.example.service` |
| 布尔变量 | 禁用 `is` 前缀 | `hasPermission`、`canExecute` |

```java
// PASS
public record Money(BigDecimal amount, Currency currency) {}
private final MarketRepository marketRepository;

// FAIL
public class user_service {}
public User Get_User_Info() {}
```

---

## 二、代码格式

- 缩进使用 4 个空格，禁止 Tab；单行不超过 120 字符
- 运算符两侧必须加空格
- if/else/for/while/do 必须使用大括号
- 成员顺序：常量 → 字段 → 构造函数 → 公共/保护/私有方法

---

## 三、常量定义

- 禁止魔法值：不允许未经预定义的常量直接出现在代码中
- 缓存 key 必须定义为常量
- `long`/`Long` 赋值数值后用大写 `L`，浮点数后缀用大写 `D`/`F`
- 常量按功能归类维护，不要一个类管理所有常量
- 固定范围值用 `enum` 替代

---

## 四、OOP 规约

- 用类名访问静态变量/方法，不用对象引用
- 覆写方法必须加 `@Override`
- 可变参数放在参数列表最后，避免定义为 `Object`
- 过时接口加 `@Deprecated` 并说明替代方案
- `equals` 比较：常量在前（`"test".equals(param)`），推荐 `Objects.equals(a, b)`
- 整型包装类比较用 `equals`，浮点数用 `BigDecimal.compareTo()`
- `BigDecimal` 用字符串构造，禁止 `new BigDecimal(double)`
- POJO 属性用包装类型，必须写 `toString`，禁止 `isXxx()` 和 `getXxx()` 并存
- 循环体内字符串拼接用 `StringBuilder`
- 严控访问范围：`private` > `protected` > `public`

---

## 五、日期时间

```java
// PASS: 小写 y 表示当天所在年
new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
// FAIL: 大写 Y 表示 week-in-which-year，跨年时返回下一年
new SimpleDateFormat("YYYY-MM-dd HH:mm:ss");
```
- 月份用大写 `M`，分钟用小写 `m`，24h 用大写 `H`
- 获取当前毫秒用 `System.currentTimeMillis()`
- JDK8+ 推荐 `Instant`、`LocalDateTime`、`DateTimeFormatter`
- 禁止 `java.sql.Date`/`Time`/`Timestamp`
- 禁止写死 365 天，用 `LocalDate.now().lengthOfYear()`

---

## 六、不可变性

- 优先使用 `record` 定义不可变数据结构
- 不可变类用 `final` 字段 + 只有 getter
- POJO 必须使用包装类型（`Integer` 不用 `int`）
- 禁止在序列化类中用 `transient` 修饰敏感属性

---

## 七、Optional 使用

```java
// PASS: find* 方法返回 Optional
Optional<Market> market = marketRepository.findBySlug(slug);

// PASS: 用 map/orElseThrow 链式处理
return market
    .map(MarketResponse::from)
    .orElseThrow(() -> new EntityNotFoundException("Market not found"));

// FAIL: 直接 get() 可能 NPE
Market m = market.get();
```

---

## 八、集合处理与 Streams

```java
// PASS: 简洁的流式操作
List<String> names = markets.stream()
    .map(Market::name)
    .filter(Objects::nonNull)
    .toList();

// PASS: 集合初始化推荐预估容量
new ArrayList<>(16);
new HashMap<>(16);
```
- 使用 `isEmpty()` 判空，不用 `size() == 0`
- 禁止 `keySet()` 遍历 Map，用 `entrySet()` 或 `Map.forEach()`
- 不要在 for-each 中 remove/add，用 `Iterator.remove()`
- 高并发用 `ConcurrentHashMap`，禁止 `HashMap`/`Hashtable`
- 覆写 `equals` 必须同时覆写 `hashCode`
- `toMap()` 必须提供 `mergeFunction`（key 重复防护），value 不能为 null
- `subList()` 返回视图，不可强转；`Arrays.asList()` 不可增删
- `addAll()` 入参必须 NPE 判断
- `Comparator` 必须满足对称性、传递性、一致性
- 集合初始化指定容量：`initialCapacity = 元素数 / 0.75 + 1`
- 避免复杂嵌套流，非必要不用 `parallelStream()`

---

## 九、异常处理

- 领域错误用非受检异常，创建特定领域异常（如 `MarketNotFoundException`）
- 避免宽泛 `catch (Exception ex)`，除非在中心位置处理
- 异常不用于流程控制，不在 finally 中 return
- 不捕获大范围异常（`Exception`/`RuntimeException`）
- 异常处理必须保留异常堆栈（`logger.error("msg: {}", param, e)`）
- `finally` 必须关闭资源（推荐 try-with-resources）
- 事务异常 catch 后需手动回滚
- RPC/二方包用 `Throwable` 捕获
- NPE 防范：包装类拆箱、数据库结果、远程调用、级联 get 一律判空

---

## 十、并发处理

- 线程必须通过线程池创建，禁止 `new Thread()`
- 线程池禁止用 `Executors`，推荐 `ThreadPoolExecutor`
- 线程/线程池必须指定有意义的名称（自定义 `ThreadFactory`）
- `ReentrantLock` 必须在 try 外加锁，finally 中释放
- 多资源加锁保持一致顺序，防止死锁
- 必须回收 `ThreadLocal`（`try-finally` + `remove()`）
- `SimpleDateFormat` 线程不安全，禁止 static；JDK8+ 用 `DateTimeFormatter`
- 并发修改加锁：冲突率 <20% 用乐观锁，否则悲观锁
- 定时任务用 `ScheduledExecutorService`，不用 `Timer`
- 共享 `Random` 用 `ThreadLocalRandom`

---

## 十一、Null 处理

- 使用 Bean 验证注解：`@NotNull`、`@NotBlank`
- 方法返回值可能为 null 时，用 `Optional<T>` 包装
- 不假设入参不为 null，必须判空

---

## 十二、日志记录

```java
// PASS: 使用 SLF4J 占位符
log.info("fetch_market slug={}", slug);
log.error("failed_fetch_market slug={}", slug, ex);

// FAIL: 字符串拼接
log.info("fetch_market slug=" + slug);
```
- 必须用 SLF4J 门面，禁止直接使用 Log4j/Logback API
- 使用占位符：`log.info("slug={}", slug)`，禁止字符串拼接
- `debug`/`info`/`trace` 输出前必须判断日志级别
- 生产环境禁止 `System.out`/`e.printStackTrace()`/debug 日志
- 异常日志必须包含现场信息 + 异常堆栈
- 用户敏感信息必须脱敏
- 避免重复打印，设置 `additivity=false`

---

## 十三、泛型和类型安全

```java
// PASS: 使用泛型，避免原始类型
public <T extends Identifiable> Map<Long, T> indexById(Collection<T> items) { ... }

// FAIL: 原始类型
public Map indexById(Collection items) { ... }
```

---

## 十四、代码坏味道

| 问题 | 解决方案 |
|------|----------|
| 长参数列表 | 使用 DTO/构建器 |
| 深度嵌套 | 提前返回（卫语句） |
| 魔法数字 | 命名常量 |
| 静态可变状态 | 优先使用依赖注入 |
| 静默捕获块 | 记录日志并处理或重新抛出 |
| 方法过长 | 提取辅助方法 |
| 类过大 | 拆分为更小的类 |

---

**记住**：保持代码意图明确、类型安全且可观察。除非证明有必要，否则优先考虑可维护性而非微优化。

## 十五、`references/` 按需加载指令

以下文件**不会自动加载**，Agent 必须根据当前任务场景**主动读取**对应文件，切根据实际场景按需加载，避免无谓的资源消耗：

| 触发场景                                                     | 必须读取的文件                    |
| ------------------------------------------------------------ | --------------------------------- |
| 需要查看某章节的完整代码示例、集合陷阱、NPE 场景、并发锁细节 | `references/detailed-examples.md` |
| 涉及控制语句、注释规约、安全规约、ORM、测试、项目结构        | `references/extended-rules.md`    |
| 创建新的 Controller / Service / DTO / 异常类等文件           | `references/templates.md`         |

**代码审查/检测场景**：仅使用本文件（SKILL.md）中的规则要点即可，**无需加载** references 文件，除非发现需要深入判断的边界场景。

*基于：阿里巴巴 Java 开发手册（黄山版）+ ECC 规范*
