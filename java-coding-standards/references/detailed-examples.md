# 详细代码示例与补充规约

> 本文件包含 `java-coding-standards` Skill 各章节的详细代码示例和补充说明。
> 核心规约要点在主 SKILL.md 中查阅，本文件提供深入示例和边界场景参考。

---

## 一、命名规范示例

### 类名示例
```java
// PASS
public class MarketService {}
public record Money(BigDecimal amount, Currency currency) {}
public class UserDO {}
public class HtmlDTO {}

// FAIL
public class user_service {}
```

### 方法名/变量示例
```java
// PASS
private final MarketRepository marketRepository;
public Market findBySlug(String slug) {}
public UserDTO getUserInfo(Long userId) {}

// FAIL
public User Get_User_Info() {}
```

### 常量示例
```java
// PASS
private static final int MAX_PAGE_SIZE = 100;
private static final String CACHE_KEY_PREFIX = "user:";

// FAIL
private static final int maxPageSize = 100;
```

---

## 二、OOP 补充示例

### equals 与比较
```java
// PASS: 常量在前，避免 NPE
"test".equals(param);
// PASS: JDK7+ 推荐
Objects.equals(a, b);
// FAIL: param 可能为 null
param.equals("test");
```
- 整型包装类比较全部使用 `equals`（-128~127 之外 `==` 失效）
- 浮点数不能用 `==` 比较，用 `BigDecimal` 或指定误差范围
- `BigDecimal` 用 `compareTo()` 比较，不用 `equals()`（精度不同结果不同）

### BigDecimal 详细规则
- 用 `new BigDecimal("0.1")` 或 `BigDecimal.valueOf(0.1)` 构造，禁止 `new BigDecimal(double)`（精度损失）
- 用 `compareTo()` 比较，不用 `equals()`（精度不同返回 false）
- 货币金额以最小货币单位且为整型存储

### POJO 规范补充
- POJO 类属性必须使用包装类型，不设默认值
- POJO 类必须写 `toString` 方法
- 禁止同时存在 `isXxx()` 和 `getXxx()` 方法
- 构造方法禁止业务逻辑，初始化放 `init()` 方法
- 序列化新增属性时不要修改 `serialVersionUID`

---

## 三、日期时间详细示例

### 格式化陷阱
```java
// PASS: 小写 y 表示当天所在年
new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
// FAIL: 大写 Y 表示 week-in-which-year，跨年时返回下一年
new SimpleDateFormat("YYYY-MM-dd HH:mm:ss");
```
- 月份用大写 `M`，分钟用小写 `m`
- 24 小时制用大写 `H`，12 小时制用小写 `h`

### 时间获取
- 获取当前毫秒：`System.currentTimeMillis()`，不用 `new Date().getTime()`
- JDK8+ 推荐用 `Instant`、`LocalDateTime`、`DateTimeFormatter`

### 禁止使用
- 禁止使用 `java.sql.Date`、`java.sql.Time`、`java.sql.Timestamp`
- 禁止写死一年为 365 天，用 `LocalDate.now().lengthOfYear()`

---

## 四、不可变性详细示例

### 优先使用 Record
```java
// PASS: 简洁、不可变、自动生成 equals/hashCode
public record MarketDto(Long id, String name, MarketStatus status) {}
```

### 不可变类
```java
// PASS: final 字段，只有 getter
public class Market {
    private final Long id;
    private final String name;
    // getters only, no setters
}
```

### POJO 包装类型
- 所有 POJO 类必须使用包装类型：`Integer` 不用 `int`
- 禁止在序列化类中使用 `transient` 关键字修饰敏感属性

---

## 五、Optional 详细示例

```java
// PASS: Return Optional from find* methods
Optional<Market> market = marketRepository.findBySlug(slug);

// PASS: Map/flatMap instead of get()
return market
    .map(MarketResponse::from)
    .orElseThrow(() -> new EntityNotFoundException("Market not found"));

// FAIL: 直接 get() 可能 NPE
Market m = market.get();
```

---

## 六、集合处理详细规约

### 流式操作示例
```java
// PASS: 简洁的流式操作
List<String> names = markets.stream()
    .map(Market::name)
    .filter(Objects::nonNull)
    .toList();

// PASS: 集合初始化推荐预估容量
new ArrayList<>(16);
new HashMap<>(16);

// FAIL: 避免复杂嵌套流；优先使用循环保证清晰度；非必要时不得使用并行流
```

### hashCode 与 equals
- 只要覆写 `equals` 就必须覆写 `hashCode`
- Set 存储的对象、Map 的自定义 key 必须覆写这两个方法

### Stream Collectors 陷阱
- `toMap()` 必须提供 `mergeFunction`，否则 key 重复时抛 `IllegalStateException`
- `toMap()` 的 value 为 null 时会抛 NPE（`HashMap.merge` 的限制）

### 集合安全陷阱
- `ArrayList.subList()` 返回的是视图，不可强转为 `ArrayList`，父集合的修改会导致子列表 `ConcurrentModificationException`
- `Collections.emptyList()` 等返回的是不可变集合，调用方不能 add/remove
- `Arrays.asList()` 返回的不能 add/remove/clear
- `addAll()` 的输入集合参数必须做 NPE 判断

### Comparator 三条件
- `compare(x,y)` 与 `compare(y,x)` 结果必须相反
- 传递性：x>y, y>z 则 x>z
- x=y 时 compare(x,z) 与 compare(y,z) 结果相同
- 不满足以上条件会导致 `IllegalArgumentException`

### 集合初始化
- 指定初始容量：`HashMap` 默认负载因子 0.75，`initialCapacity = 元素数 / 0.75 + 1`
- `Map` 集合 K/V 是否允许 null 要清楚（`ConcurrentHashMap` 不允许 null key/value）

---

## 七、异常处理详细示例

### 异常使用示例
```java
// PASS: 领域异常
throw new MarketNotFoundException(slug);

// PASS: 完整的异常处理
try {
    // 业务逻辑
} catch (IOException e) {
    logger.error("文件处理异常: {}", fileName, e);
    throw new BusinessException("文件处理失败", e);
}
```

### NPE 场景总结
- 基本类型 return 包装类对象时，自动拆箱可能 NPE
- 数据库查询结果可能为 null
- 集合元素即使 isNotEmpty 也可能含 null
- 远程调用返回对象一律判空
- 级联调用 `obj.getA().getB()` 易产生 NPE，用 Optional 或逐层判空

### 资源与事务
- `finally` 块必须关闭资源对象、流对象（推荐 try-with-resources）
- 事务场景中，异常被 catch 后如需回滚，必须手动回滚事务
- 捕获异常与抛异常必须完全匹配，或捕获异常是抛异常的父类
- 调用 RPC / 二方包时，用 `Throwable` 捕获（可能抛出 `NoSuchMethodError`）

---

## 八、并发处理详细规约

### 锁的详细规范
- 高并发锁的粒度：方法锁 > 对象锁 > 类锁
- 使用 `ReentrantLock` 时必须在 finally 中释放锁
- 不要在静态方法中使用同步锁
- 对多个资源/表/对象加锁时，必须保持一致的加锁顺序，否则可能死锁
- `ReentrantLock` 必须在 try 代码块之外加锁，加锁方法与 try 之间不能有可能抛异常的代码
- 尝试机制 `tryLock()` 时，进入业务前必须先判断当前线程是否持有锁

### 线程命名与 ThreadLocal
- 创建线程/线程池时必须指定有意义的线程名称（自定义 `ThreadFactory`），方便排查
- 必须回收自定义的 `ThreadLocal` 变量，用 `try-finally` 调用 `remove()`，尤其在线程池场景下

### 其他并发规范
- 单例对象及其方法必须保证线程安全
- `SimpleDateFormat` 线程不安全，禁止定义为 static 变量；JDK8+ 用 `DateTimeFormatter`
- 并发修改同一记录时必须加锁，冲突率 <20% 用乐观锁，否则用悲观锁
- 多线程定时任务用 `ScheduledExecutorService`，不用 `Timer`（一个任务异常会影响其他任务）
- 避免 `Random` 实例被多线程共享，用 `ThreadLocalRandom`

---

## 九、Null 处理详细示例

```java
// PASS: 使用 Bean 验证
@NotNull
@NotBlank
private String name;

// PASS: 方法返回值判空
public Optional<Market> findBySlug(String slug) {
    // 实现
}

// FAIL: 接受 null 作为有效参数
public void process(String data) {
    // 不要假设 data 不为 null
}
```

---

## 十、日志记录详细示例

### 日志输出示例
```java
// PASS: 使用 SLF4J 占位符
private static final Logger log = LoggerFactory.getLogger(MarketService.class);
log.info("fetch_market slug={}", slug);
log.error("failed_fetch_market slug={}", slug, ex);

// FAIL: 字符串拼接
log.info("fetch_market slug=" + slug);
```

### 日志级别
- `ERROR`：错误事件，系统仍能运行
- `WARN`：潜在的有害情形
- `INFO`：运行时信息
- `DEBUG`：调试级别信息

### 日志详细规范
- 应用不可直接使用 Log4j / Logback API，必须用 SLF4J 门面
- `debug` / `info` / `trace` 级别日志输出前，必须做日志级别开关判断（避免无谓的字符串拼接开销）
- 生产环境禁止使用 `System.out` / `System.err` / `e.printStackTrace()`
- 异常日志必须包含案发现场信息 + 异常堆栈（`logger.error("msg: {}", param, e)`）
- 日志打印时禁止直接用 JSON 工具将对象转 String（get 方法可能抛异常影响业务）
- 避免重复打印日志，设置 `additivity=false`
- 用户敏感信息必须脱敏处理
- 生产环境禁止输出 debug 日志；warn 日志注意输出量

---

## 十一、泛型与类型安全示例

```java
// PASS: 使用泛型，避免原始类型
public <T extends Identifiable> Map<Long, T> indexById(Collection<T> items) { ... }

// FAIL: 原始类型
public Map indexById(Collection items) { ... }
```

---

## 十二、代码坏味道

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

## 十三、格式化和风格

- 一致地使用 4 个空格（项目标准）
- 每个文件一个公共顶级类型
- 保持方法简短且专注；提取辅助方法
- 注释说明"为什么"而不是"做了什么"
