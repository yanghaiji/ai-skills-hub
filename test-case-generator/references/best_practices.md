# 测试最佳实践

## 目录

1. [命名规范](#命名规范)
2. [测试结构](#测试结构)
3. [测试数据管理](#测试数据管理)
4. [Mock使用规范](#mock使用规范)
5. [断言最佳实践](#断言最佳实践)
6. [测试维护](#测试维护)

---

## 命名规范

### 测试文件命名
```python
# 好的命名
test_user_service.py
test_authentication.py
test_payment_processing.py

# 不好的命名
tests.py
test.py
user.py
```

### 测试类命名
```python
# 好的命名
class TestUserLogin:
class TestPaymentProcessing:
class TestDatabaseConnection:

# 不好的命名
class Tests:
class TestClass:
class MyClass:
```

### 测试方法命名
```python
# 好的命名（Given-When-Then风格）
def test_should_return_user_when_valid_id():
def test_should_raise_exception_when_user_not_found():
def test_should_redirect_to_login_when_not_authenticated():

# 好的命名（行为风格）
def test_user_login_success():
def test_user_login_invalid_password():
def test_user_login_account_locked():

# 不好的命名
def test_login():
def test_1():
def test_function():
```

---

## 测试结构

### AAA模式
```python
def test_example():
    # Arrange - 准备
    user = User(name="John", email="john@example.com")
    
    # Act - 执行
    result = user.get_display_name()
    
    # Assert - 验证
    assert result == "John (john@example.com)"
```

### 测试方法长度
```python
# 好的：简短、专注
def test_should_validate_email():
    assert validate_email("test@example.com") == True

# 不好的：过长、复杂
def test_user_registration():
    # 准备数据
    # 验证输入
    # 创建用户
    # 发送邮件
    # 记录日志
    # 返回结果
    pass
```

### 测试数量
```python
# 好的：一个测试一个断言点
def test_should_validate_email_format():
    assert validate_email("test@example.com") == True

def test_should_reject_invalid_email():
    assert validate_email("invalid") == False

# 不好的：一个测试多个断言点
def test_email_validation():
    assert validate_email("test@example.com") == True
    assert validate_email("invalid") == False
    assert validate_email("") == False
    assert validate_email(None) == False
```

---

## 测试数据管理

### 使用Fixtures
```python
@pytest.fixture
def sample_user():
    return User(
        id=1,
        name="John Doe",
        email="john@example.com"
    )

def test_user_display_name(sample_user):
    assert sample_user.get_display_name() == "John Doe"
```

### 使用工厂模式
```python
class UserFactory:
    _id_counter = 1
    
    @classmethod
    def create(cls, **kwargs):
        defaults = {
            "id": cls._id_counter,
            "name": f"User {cls._id_counter}",
            "email": f"user{cls._id_counter}@example.com"
        }
        defaults.update(kwargs)
        cls._id_counter += 1
        return User(**defaults)

def test_user_creation():
    user = UserFactory.create()
    assert user.id == 1
```

### 使用参数化测试
```python
@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("invalid-email", False),
    ("", False),
    ("test@", False),
])
def test_email_validation(email, expected):
    assert validate_email(email) == expected
```

---

## Mock使用规范

### 何时Mock
- ✅ 外部API调用
- ✅ 数据库操作
- ✅ 文件系统操作
- ✅ 时间相关操作
- ❌ 简单的计算函数
- ❌ 数据传输对象（DTO）

### Mock示例
```python
from unittest.mock import Mock, patch, MagicMock

# Mock外部API
def test_api_call():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "ok"}
        
        result = call_external_api()
        
        assert result["status"] == "ok"
        mock_get.assert_called_once()

# Mock数据库
def test_database_operation():
    with patch('database.connect') as mock_db:
        mock_db.return_value.execute.return_value = Mock(fetchall=Mock(return_value=[]))
        
        result = get_all_users()
        
        assert result == []
```

### Mock最佳实践
```python
# 好的：Mock具体的行为
mock_service.get_user.return_value = User(id=1, name="John")

# 不好的：Mock实现细节
mock_service.get_user = Mock(return_value=User(id=1, name="John"))
```

---

## 断言最佳实践

### 使用合适的断言方法
```python
# 好的：使用描述性断言
assert result is not None
assert len(items) == 3
assert "error" in error_message.lower()

# 不好的：使用模糊断言
assert result  # 不够明确
assert items  # 不够明确
```

### 使用自定义断言消息
```python
def test_user_age():
    user = User(age=25)
    assert user.age >= 0, f"用户年龄应为非负数，实际为 {user.age}"
```

### 使用pytest断言重写
```python
# pytest会自动重写assert语句，提供更好的错误信息
def test_list_comparison():
    assert [1, 2, 3] == [1, 2, 4]  # 会显示详细的差异信息
```

---

## 测试维护

### 测试代码质量
1. **保持测试简单**：测试代码应该比生产代码更简单
2. **消除重复**：使用fixtures和辅助函数
3. **及时重构**：当测试变得难以维护时进行重构

### 测试文档
```python
def test_user_registration():
    """
    测试用户注册功能
    
    测试场景：
    1. 正常注册流程
    2. 验证邮箱格式
    3. 检查用户名唯一性
    
    预期结果：
    - 成功注册并返回用户对象
    - 发送验证邮件
    - 记录注册日志
    """
    pass
```

### 测试分类
```python
# 使用标记分类测试
@pytest.mark.smoke
def test_critical_feature():
    pass

@pytest.mark.regression
def test_bug_fix():
    pass

# 运行特定分类的测试
# pytest -m smoke
# pytest -m regression
```

---

## 常见错误和解决方案

### 1. 测试耦合
**问题**：测试之间相互依赖
**解决**：确保每个测试独立，使用独立的测试数据

### 2. 测试不稳定
**问题**：测试结果随机变化
**解决**：消除时间依赖、网络依赖，使用Mock

### 3. 测试覆盖不足
**问题**：只测试正常情况
**解决**：添加边界测试、异常测试

### 4. 测试维护成本高
**问题**：测试代码难以理解
**解决**：简化测试逻辑，添加注释，使用清晰的命名

---

## 测试工具推荐

### Python测试工具
- **pytest**：测试框架
- **pytest-cov**：覆盖率报告
- **pytest-html**：HTML报告
- **pytest-mock**：Mock工具
- **factory-boy**：测试数据工厂
- **faker**：假数据生成

### 集成工具
- **tox**：测试环境管理
- **pre-commit**：代码质量检查
- **GitHub Actions**：CI/CD集成
