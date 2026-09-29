# 测试模式参考

## 目录

1. [测试金字塔](#测试金字塔)
2. [测试模式](#测试模式)
3. [设计模式](#设计模式)
4. [测试策略](#测试策略)

---

## 测试金字塔

测试金字塔描述了不同层次测试的比例关系：

```
        /\
       /  \  E2E测试（少）
      /    \
     /------\  集成测试（中）
    /        \
   /----------\  单元测试（多）
```

### 单元测试
- **目标**：验证单个函数或类的行为
- **比例**：约70%
- **特点**：快速、独立、可重复

### 集成测试
- **目标**：验证多个组件之间的交互
- **比例**：约20%
- **特点**：测试组件边界、依赖注入

### 端到端测试（E2E）
- **目标**：验证完整系统的工作流程
- **比例**：约10%
- **特点**：模拟真实用户场景

---

## 测试模式

### 1. AAA模式（Arrange-Act-Assert）

最常用的测试结构：

```python
def test_function():
    # Arrange - 准备测试数据
    input_data = "test"
    expected = "expected"
    
    # Act - 执行测试操作
    result = function_under_test(input_data)
    
    # Assert - 验证测试结果
    assert result == expected
```

### 2. Given-When-Then模式

BDD（行为驱动开发）常用模式：

```python
def test_behavior():
    # Given - 给定前提条件
    given_user_is_logged_in()
    
    # When - 当执行某个操作
    when_user_clicks_logout()
    
    # Then - 那么应该发生什么
    then_user_should_be_redirected_to_login()
```

### 3. 模式匹配模式

用于测试复杂对象结构：

```python
def test_complex_object():
    result = get_user_data()
    
    assert result == {
        "id": 1,
        "name": "John",
        "email": "john@example.com"
    }
```

### 4. 参数化测试模式

减少重复代码，测试多种输入：

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

### 5. 夹具模式（Fixture）

管理测试前置和后置条件：

```python
@pytest.fixture
def setup_database():
    # Setup
    db = create_test_database()
    yield db
    # Teardown
    db.cleanup()
```

---

## 设计模式

### 1. Page Object模式

用于UI测试，封装页面元素和操作：

```python
class LoginPage:
    def __init__(self, driver):
        self.driver = driver
    
    def login(self, username, password):
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "login-btn").click()
```

### 2. Builder模式

用于构建复杂测试对象：

```python
class UserBuilder:
    def __init__(self):
        self.user = {"name": "default", "age": 25}
    
    def with_name(self, name):
        self.user["name"] = name
        return self
    
    def with_age(self, age):
        self.user["age"] = age
        return self
    
    def build(self):
        return self.user
```

### 3. Factory模式

用于创建测试数据：

```python
class UserFactory:
    @staticmethod
    def create(**kwargs):
        default_user = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com"
        }
        default_user.update(kwargs)
        return User(**default_user)
```

### 4. Mock模式

模拟外部依赖：

```python
from unittest.mock import Mock, patch

def test_api_call():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        
        result = call_api()
        
        assert result == {"status": "ok"}
```

---

## 测试策略

### 1. 测试优先级策略

根据重要性确定测试优先级：

- **P0 - 冒烟测试**：核心功能，必须通过
- **P1 - 回归测试**：重要功能，版本发布前必须通过
- **P2 - 验收测试**：一般功能，有时间时执行
- **P3 - 探索测试**：边界情况，资源允许时执行

### 2. 测试覆盖策略

- **代码覆盖率**：目标 ≥ 80%
- **分支覆盖率**：目标 ≥ 70%
- **需求覆盖率**：目标 100%

### 3. 测试数据策略

- **正常数据**：符合预期格式和范围
- **边界数据**：最小值、最大值、边界值
- **异常数据**：无效输入、空值、超长数据

### 4. 测试环境策略

- **开发环境**：开发人员自测
- **测试环境**：QA团队测试
- **预生产环境**：验收测试
- **生产环境**：线上监控

---

## 测试反模式

### 1. 测试脆弱性
- ❌ 测试依赖外部系统状态
- ❌ 测试顺序依赖
- ❌ 测试依赖特定时间

### 2. 测试不确定性
- ❌ 测试结果随机变化
- ❌ 测试数据污染
- ❌ 测试环境不稳定

### 3. 测试维护问题
- ❌ 测试代码重复
- ❌ 测试逻辑复杂
- ❌ 测试文档缺失

---

## 最佳实践总结

1. **保持测试独立性**：每个测试应该独立运行
2. **测试应该快速**：单元测试应在毫秒级完成
3. **测试应该可重复**：多次运行结果一致
4. **测试应该自验证**：自动判断通过/失败
5. **测试应该及时**：在代码编写后立即编写测试
6. **测试应该简单**：测试代码应易于理解
7. **测试应该全面**：覆盖正常、边界、异常场景
8. **测试应该自动化**：集成到CI/CD流程
