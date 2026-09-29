---
name: unit-testing
description: "单元测试规范：先自动发现项目中已有测试模式并保持一致，再按最佳实践编写。覆盖测试原则、命名、Mock、覆盖率、模式。触发条件：编写单元测试、测试用例、创建单测、生成测试时。"
metadata:
  author: Yanghaiji
  version: "2.0.0"
---

# 单元测试规范

适用于任何语言和框架的单元测试最佳实践。

## 何时激活

* 编写单元测试时
* 重构代码需要补充测试时
* **每次让 AI 编写测试时必须触发此规范**

---

## 一、核心工作流（必须执行）

**不预设任何固定模式，先学习项目已有测试，再编写新测试。**

当用户要求创建单元测试时，**必须严格按以下步骤执行**，不可跳过：

### Step 1: 发现已有测试（不可跳过）

在编写任何测试代码之前，必须先找到并阅读项目中已有的测试文件。

**查找策略（按优先级）：**

1. **同模块同层级**：在被测类所在模块的 `test` 目录下，查找与被测类相同包路径的已有测试文件
2. **同模块其他包**：在当前模块的 `test` 目录下查找其他包的测试文件
3. **全项目搜索**：搜索整个项目中所有测试文件

**常见测试文件定位方式：**
- 测试目录：`src/test/`、`tests/`、`__tests__/`、`.test/`、`spec/`
- 测试命名：`*Test`、`*Spec`、`test_*`、`*_test`、`*.test.*`

### Step 2: 分析已有测试模式（不可跳过）

阅读找到的 2-3 个已有测试文件，提取以下维度的模式：

```
需要提取的模式信息：
├── 测试框架：JUnit4 / JUnit5 / pytest / Jest / Go testing / ...
├── Mock 框架：Mockito / unittest.mock / jest.mock / ...
├── 初始化方式：注解驱动 / 手动构造 / 基类继承 / ...
├── 依赖注入 Mock 方式：@Mock+@InjectMocks / 构造器注入 / ...
├── 静态方法/模块处理：MockedStatic / jest.mock / patch / ...
├── 断言风格：assertEquals / assertThat / expect().toBe / ...
├── 测试方法命名：testXxx / xxx_should_xxx / 中文注释 / ...
├── setUp/tearDown：@BeforeEach / @Before / fixture / ...
├── 特殊处理：统一响应体 Mock / 事务 / 安全上下文 / ...
└── 测试数据构造：直接 new / Builder / Factory / Fixture / ...
```
详细的方式参考`references/examples.md`

### Step 3: 分析被测类

1. 读取被测类源码
2. 识别所有依赖（构造器注入、字段注入、方法参数等）
3. 列出所有需要测试的 public 方法
4. 识别方法中的分支逻辑、异常处理、边界条件

### Step 4: 编写测试

**严格按照 Step 2 中提取到的模式编写**，确保与已有测试风格完全一致。
同时遵循下面的最佳实践原则。

### Step 5: 验证

- 检查 import 是否完整
- 检查是否能编译/运行通过
- 检查是否遵循了已有测试的所有约定

---

## 一、核心原则

### 1.1 测试金字塔
```
        /\
       /  \  E2E 测试（少）
      /    \
     /------\  集成测试（中）
    /        \
   /----------\  单元测试（多）
```

### 1.2 FIRST 原则
- **Fast** - 快速执行
- **Independent** - 测试独立，无依赖
- **Repeatable** - 可重复执行
- **Self-validating** - 自动验证结果
- **Timely** - 及时编写（TDD）

---

## 二、测试命名

### 2.1 命名格式（优先采用项目中已有的命名风格）

**风格 A — BDD 下划线式**（Java/Python 常见）：
```
方法名_场景_预期结果

示例：
getUser_validId_returnsUser
getUser_invalidId_throwsNotFoundException
getUser_nullId_throwsNullPointerException
```

**风格 B — test 前缀式**（传统 Java 常见）：
```
test方法名
test方法名_场景

示例：
testGetUser
testGetUser_validId
testGetUser_nullId_throwsException
```

**风格 C — should 式**（JS/TS 常见）：
```
should_预期结果_when_条件

示例：
should_returnUser_when_validId
should_throwException_when_userNotFound
```

**规则：如果项目中已有测试使用了某种命名风格，新测试必须保持一致。**

### 2.2 中文命名（可选，部分项目使用）
```java
// 当输入有效ID时，应返回用户
@Test
void 当输入有效ID时_应返回用户() {
    // ...
}
```

---

## 三、测试结构（AAA 模式）

每个测试方法遵循 **Arrange-Act-Assert** 三段式：

```java
@Test
void should_return_user_when_valid_id() {
    // Arrange（准备）
    Long userId = 1L;
    User expectedUser = new User(userId, "John");
    when(userRepository.findById(userId)).thenReturn(Optional.of(expectedUser));
    
    // Act（执行）
    User result = userService.getUser(userId);
    
    // Assert（断言）
    assertThat(result).isNotNull();
    assertThat(result.getName()).isEqualTo("John");
}
```

注释语言跟随项目约定（中文项目用中文注释，英文项目用英文注释）。

---

## 四、断言规范

### 4.1 优先使用项目已有的断言风格

如果项目用 AssertJ，就用 AssertJ；如果项目用 JUnit 原生断言，就用原生断言。**一致性优先。**

### 4.2 断言最佳实践（通用）
```java
// 流式断言更可读（AssertJ 风格）
assertThat(user.getName()).isEqualTo("John");
assertThat(user.getEmail()).isNotEmpty();
assertThat(users).hasSize(3).extracting(User::getName).contains("John");

// 提供清晰的失败信息
assertThat(user)
    .as("用户ID为%s时应返回用户", userId)
    .isNotNull();
```

### 4.3 断言原则
- 断言要验证行为，不要断言实现细节
- 一个测试聚焦一个断言点（可以有多个 assert，但验证的是同一个行为）
- 避免只断言"不报错"而不验证结果

---

## 五、Mock 规范

### 5.1 何时 Mock
| 场景 | 是否 Mock | 原因 |
|------|-----------|------|
| 数据库操作 | ✅ | 速度、环境依赖 |
| 外部 API | ✅ | 网络、第三方 |
| 文件系统 | ✅ | IO 依赖 |
| 工具类（纯函数） | ❌ | 简单、快速、无副作用 |
| 纯业务逻辑 | ❌ | 直接测试 |
| 值对象 / DTO | ❌ | 无逻辑 |

### 5.2 Mock 最佳实践
```java
// ✅ 只 Mock 必要的外部依赖
@Mock
private UserRepository userRepository;

@Mock
private EmailService emailService;

@InjectMocks
private UserService userService;

// ❌ 禁忌
// ❌ 不要 Mock 被测对象自身的方法
// ❌ 不要过度 Mock（测试实现而非行为）
// ❌ 不要在每个测试中都 Mock 所有依赖
```

### 5.3 Verify 调用验证
```java
// 验证方法被调用
verify(userRepository).save(any(User.class));

// 验证调用次数
verify(emailService, times(1)).send(anyString());

// 验证从未调用
verify(logService, never()).log(anyString());
// 或
verifyNoInteractions(logService);
```

---

## 六、测试覆盖

### 6.1 覆盖率参考
| 类型 | 建议目标 |
|------|----------|
| 核心业务逻辑 | ≥ 80% |
| 工具类 | ≥ 90% |
| Controller / API 层 | ≥ 70% |
| 整体项目 | ≥ 70% |

> 注意：如果项目有自己的覆盖率配置，以项目配置为准。

### 6.2 每个 public 方法至少覆盖
- [ ] 正常流程（Happy Path）
- [ ] 边界条件（空值、空集合、极值）
- [ ] 异常情况（依赖抛异常时的行为）

根据方法复杂度酌情增加：
- 不同分支的覆盖
- 不同输入组合（考虑参数化测试）
- 并发场景（如适用）

### 6.3 不追求覆盖的情况
- 简单的 getter/setter
- 配置类
- 框架代码
- 日志代码

---

## 七、测试模式

### 7.1 参数化测试
```java
// Java - JUnit 5
@ParameterizedTest
@CsvSource({
    "1, true",
    "0, false",
    "-1, false"
})
void should_validate_age(int age, boolean expected) {
    assertThat(ageService.isValidAge(age)).isEqualTo(expected);
}
```

### 7.2 异常测试
```java
// Java - AssertJ
@Test
void should_throw_exception_when_user_not_found() {
    when(userRepository.findById(999L)).thenReturn(Optional.empty());
    
    assertThatThrownBy(() -> userService.getUser(999L))
        .isInstanceOf(UserNotFoundException.class)
        .hasMessageContaining("999");
}

// Java - JUnit 5
@Test
void should_throw_exception_when_user_not_found() {
    when(userRepository.findById(999L)).thenReturn(Optional.empty());
    
    assertThrows(UserNotFoundException.class, () -> {
        userService.getUser(999L);
    });
}
```

### 7.3 测试替身
```java
// Fake - 简化实现（适用于复杂接口）
public class FakeUserRepository implements UserRepository {
    private Map<Long, User> store = new HashMap<>();
    
    @Override
    public Optional<User> findById(Long id) {
        return Optional.ofNullable(store.get(id));
    }
}
```

---

## 八、测试禁忌

| 禁忌 | 原因 |
|------|------|
| 测试依赖执行顺序 | 测试应独立 |
| 硬编码测试数据 | 使用工厂或构造器 |
| 测试中 sleep | 使用 Awaitility 或轮询 |
| 捕获异常后断言空 | 应该直接断言异常 |
| 过度断言 | 测试行为而非实现细节 |
| 测试间共享可变状态 | 每个测试独立 setup |
| 忽略已有测试风格 | 一致性是第一优先级 |

---

## 代码审查清单

- [ ] 已读取并分析了项目中至少 2 个已有测试文件
- [ ] 新测试的风格与已有测试完全一致（框架、注解、Mock、断言、命名）
- [ ] 测试命名清晰，遵循项目命名约定
- [ ] 遵循 AAA 模式
- [ ] 被测类的所有依赖都已正确 Mock
- [ ] 项目中特有的约定已正确处理（如统一响应体、静态方法等）
- [ ] 每个 public 方法至少有正常路径 + 异常路径测试
- [ ] 边界条件已覆盖
- [ ] 无过度 Mock
- [ ] 测试独立可重复
- [ ] 测试可编译/运行通过

---

*参考：FIRST Principles + AAA Pattern + Mockito + Testing Patterns*
