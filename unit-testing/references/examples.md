# 测试模式识别参考

本文件帮助识别项目中常见的测试模式类型。在 Step 2（分析已有测试模式）时参考。

---

## 如何判断应使用哪种模式

阅读已有测试后，对照以下特征匹配：

### 特征 1：初始化方式

| 观察到的特征 | 对应模式 |
|---|---|
| setUp 中调用 `MockitoAnnotations.openMocks(this)` 或 `initMocks(this)` | MockitoAnnotations 模式 |
| 类上有 `@ExtendWith(MockitoExtension.class)` 或 `@RunWith(MockitoJUnitRunner.class)` | 注解驱动模式 |
| 测试类继承某个 BaseTest / AbstractTest 基类 | 基类继承模式 |
| 无特殊注解，直接 `new` 被测对象 | 手动构造模式 |
| 使用 `@SpringBootTest` 注解 | Spring 集成测试模式 |

### 特征 2：依赖注入方式

| 观察到的特征 | 对应做法 |
|---|---|
| Mock 用 `@Mock`，被测对象用 `@InjectMocks` | 注解自动注入 |
| Mock 用 `@Mock`，被测对象在 setUp 中手动 `new` 并传入 | 构造器手动注入 |
| 无 Mock 框架，直接传入真实对象或 stub | 无 Mock 模式 |

### 特征 3：静态方法处理

| 观察到的特征 | 对应做法 |
|---|---|
| 使用 `MockedStatic<Xxx>` + try-with-resources | 方法级静态 Mock |
| 在 setUp 中 `mockStatic`，在 tearDown 中 `close` | 类级静态 Mock |
| 不处理静态方法 | 无需处理 |

### 特征 4：统一响应体

| 观察到的特征 | 对应做法 |
|---|---|
| 有 `setupResultMock()` 或类似的统一 Mock 方法 | 需要 Mock 统一响应体的静态方法 |
| 直接断言返回值 | 无需特殊处理 |
| 使用 MockMvc 的 `status().isOk()` | HTTP 层验证 |

### 特征 5：断言风格

| 观察到的特征 | 对应做法 |
|---|---|
| `assertEquals` / `assertTrue` / `assertThrows` | JUnit 原生断言 |
| `assertThat(...).isEqualTo(...)` | AssertJ 流式断言 |
| `expect(...).toBe(...)` | Jest/Vitest 风格 |
| `verify(mock).method()` 作为主要验证手段 | 交互验证为主 |

### 特征 6：测试命名

| 观察到的特征 | 对应做法 |
|---|---|
| `testMethodName` | 简单前缀式 |
| `testMethodName_scenario` | 前缀+场景 |
| `methodName_scenario_ShouldExpected` | BDD 风格 |
| `test_method_name` | 下划线分隔 |

---

## 常见项目类型速查

### Java + Spring Boot（新项目）

- 框架：JUnit 5 + Mockito
- 关键：注意统一响应体（如 `Result`）的静态方法 Mock
- 关键：注意 `@Autowired` 字段需要 `@Mock`
- 可选：MockMvc 做 HTTP 层测试

### Java + Spring Boot（旧项目）

- 框架：JUnit 4 + Mockito + PowerMock
- 关键：`@RunWith(MockitoJUnitRunner.class)` 或 `MockitoAnnotations.initMocks(this)`
- 关键：`@Before` / `@After` 而非 `@BeforeEach` / `@AfterEach`

### TypeScript / JavaScript

- 框架：Jest / Vitest / Mocha
- 关键：`jest.mock()` / `vi.mock()` 做模块 Mock
- 关键：`describe` / `it` / `expect` 结构

### Python

- 框架：pytest / unittest
- 关键：`unittest.mock.patch` 做 Mock
- 关键：`fixture` 做测试数据准备

### Go

- 框架：标准 `testing` 包 + testify
- 关键：表驱动测试（table-driven tests）
- 关键：接口 Mock 通过手写 struct 实现
