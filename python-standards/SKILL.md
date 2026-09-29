---
name: python-standards
description: "Python 编码规范：类型注解、代码风格、项目结构、测试、性能优化。触发条件：编写Python代码、创建模块、实现功能、代码审查时。"
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# Python 编码规范

适用于 Python 3.10+ 的现代 Python 开发标准。

## 何时激活

* 编写或审查 Python 代码时
* 创建模块、包或项目时
* 实现业务逻辑或工具函数时
* **每次让AI编写Python代码时必须触发此规范**

## 核心原则

* 可读性优先：代码是写给人看的
* 显式优于隐式：明确表达意图
* 简单优于复杂：KISS 原则
* 一种最好的方法：约定优于配置

---

## 一、代码风格 (PEP 8)

### 1.1 缩进与空格
- 使用 4 个空格缩进，禁止 Tab
- 行宽限制 88 字符（Black 格式化器默认）
- 二元运算符两侧加空格

### 1.2 命名规范
```python
# PASS
class UserService:           # 类名：PascalCase
    MAX_RETRY_COUNT = 3      # 常量：UPPER_SNAKE_CASE
    
    def get_user_info(self): # 方法：snake_case
        user_name = "test"   # 变量：snake_case
        is_valid = True      # 布尔：is/has/can 前缀

# FAIL
class user_service:          # 错误：PascalCase
    maxRetryCount = 3        # 错误：camelCase
```

### 1.3 导入规范
```python
# PASS: 导入顺序
import os
import sys
from pathlib import Path
from typing import Optional, List

import requests
from fastapi import FastAPI

from myproject.models import User
from myproject.services import UserService

# FAIL: 混乱的导入
import os, sys
from myproject.models import User
import requests
```

---

## 二、类型注解

### 2.1 函数签名
```python
# PASS: 完整类型注解
def get_user(user_id: int, include_posts: bool = False) -> Optional[User]:
    pass

# PASS: 复杂类型
def process_items(
    items: List[dict[str, any]],
    filter_fn: Callable[[dict], bool]
) -> list[dict]:
    pass

# PASS: 异步函数
async def fetch_data(url: str) -> dict:
    pass
```

### 2.2 变量注解
```python
# PASS: 变量类型注解
user_name: str = "John"
age: int = 25
scores: list[int] = [100, 95, 87]
user_map: dict[str, User] = {}

# PASS: 使用 Final 表示常量
from typing import Final
MAX_SIZE: Final = 100
```

### 2.3 类型别名
```python
from typing import TypeAlias

# PASS: 使用 TypeAlias
Vector: TypeAlias = list[float]
Matrix: TypeAlias = list[Vector]
UserMap: TypeAlias = dict[str, User]
```

### 2.4 Protocol（鸭子类型）
```python
from typing import Protocol

# PASS: 使用 Protocol 定义接口
class Drawable(Protocol):
    def draw(self) -> None: ...

def render(shape: Drawable) -> None:
    shape.draw()
```

---

## 三、数据类与类型

### 3.1 使用 dataclass
```python
from dataclasses import dataclass, field
from typing import ClassVar

# PASS: 数据类
@dataclass
class User:
    id: int
    name: str
    email: str
    is_active: bool = True
    
    # 类变量不参与 dataclass
    MAX_NAME_LENGTH: ClassVar[int] = 100

# PASS: 不可变数据类
@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

### 3.2 使用 Pydantic（数据验证）
```python
from pydantic import BaseModel, Field, EmailStr

# PASS: Pydantic 模型
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)

# 使用
user = UserCreate(name="John", email="john@example.com", age=25)
```

### 3.3 枚举类型
```python
from enum import Enum, IntEnum

# PASS: 字符串枚举
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

# PASS: 整数枚举
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
```

---

## 四、函数设计

### 4.1 函数长度
```python
# PASS: 短小函数，单一职责
def validate_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1]

def get_user_display_name(user: User) -> str:
    return f"{user.first_name} {user.last_name}"

# FAIL: 函数过长
def process_user(user_id: int, action: str, notify: bool, ...):
    # 100+ 行代码
    pass
```

### 4.2 参数设计
```python
# PASS: 使用关键字参数
def create_user(
    name: str,
    email: str,
    *,
    age: Optional[int] = None,
    role: UserRole = UserRole.USER
) -> User:
    pass

# PASS: 参数解构
@dataclass
class CreateUserRequest:
    name: str
    email: str
    age: Optional[int] = None
    role: UserRole = UserRole.USER

def create_user(request: CreateUserRequest) -> User:
    pass
```

### 4.3 返回值
```python
from typing import Union, TypeAlias

# PASS: 使用 Union 或 TypeAlias
Result: TypeAlias = Union[User, ErrorMessage]

def get_user(user_id: int) -> Result:
    if user_id < 0:
        return ErrorMessage("Invalid ID")
    return User(id=user_id, name="John")

# PASS: 使用元组返回多个值
def divide(a: float, b: float) -> tuple[float, bool]:
    if b == 0:
        return 0.0, False
    return a / b, True
```

---

## 五、异常处理

### 5.1 异常定义
```python
# PASS: 自定义异常层次
class AppError(Exception):
    """应用基础异常"""
    pass

class ValidationError(AppError):
    """验证错误"""
    pass

class NotFoundError(AppError):
    """未找到错误"""
    pass

class UserNotFoundError(NotFoundError):
    """用户未找到"""
    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} not found")
        self.user_id = user_id
```

### 5.2 异常使用
```python
# PASS: 精确捕获
try:
    user = get_user(user_id)
except UserNotFoundError as e:
    logger.warning(f"User not found: {e.user_id}")
    raise
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise AppError("Failed to fetch user") from e

# FAIL: 捕获所有异常
try:
    # something
except:
    pass
```

### 5.3 上下文管理器
```python
from contextlib import contextmanager

# PASS: 使用上下文管理器管理资源
@contextmanager
def database_connection():
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()

# 使用
with database_connection() as conn:
    conn.execute("SELECT * FROM users")
```

---

## 六、类设计

### 6.1 类结构
```python
from dataclasses import dataclass
from typing import ClassVar

# PASS: 类成员顺序
class UserService:
    # 1. 类变量
    MAX_RETRY: ClassVar[int] = 3
    
    # 2. 实例变量（通过 __init__）
    def __init__(self, db: Database):
        self._db = db
        self._cache: dict[int, User] = {}
    
    # 3. 静态方法
    @staticmethod
    def validate_email(email: str) -> bool:
        return "@" in email
    
    # 4. 类方法
    @classmethod
    def from_config(cls, config: Config) -> "UserService":
        db = Database(config.db_url)
        return cls(db)
    
    # 5. 属性
    @property
    def is_connected(self) -> bool:
        return self._db.is_connected
    
    # 6. 公共方法
    def get_user(self, user_id: int) -> Optional[User]:
        pass
    
    # 7. 私有方法
    def _fetch_from_cache(self, key: int) -> Optional[User]:
        pass
```

### 6.2 魔术方法
```python
# PASS: 实现有用的魔术方法
@dataclass
class Vector:
    x: float
    y: float
    
    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)
    
    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y
```

---

## 七、迭代器与生成器

### 7.1 生成器函数
```python
from typing import Generator, Iterator

# PASS: 使用生成器处理大数据
def read_large_file(file_path: str) -> Generator[str, None, None]:
    with open(file_path, "r") as f:
        for line in f:
            yield line.strip()

# PASS: 无限序列
def fibonacci() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
```

### 7.2 迭代器协议
```python
# PASS: 实现迭代器类
class Countdown:
    def __init__(self, start: int):
        self.start = start
    
    def __iter__(self) -> Iterator[int]:
        return self
    
    def __next__(self) -> int:
        if self.start <= 0:
            raise StopIteration
        self.start -= 1
        return self.start + 1
```

---

## 八、异步编程

### 8.1 async/await
```python
import asyncio
from typing import AsyncGenerator

# PASS: 异步函数
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# PASS: 异步生成器
async def async_range(start: int, stop: int) -> AsyncGenerator[int, None]:
    for i in range(start, stop):
        await asyncio.sleep(0.1)
        yield i

# PASS: 并发执行
async def fetch_all(urls: list[str]) -> list[dict]:
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### 8.2 异步上下文管理器
```python
# PASS: 异步资源管理
class AsyncDatabase:
    async def __aenter__(self):
        self.connection = await create_connection()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()

# 使用
async with AsyncDatabase() as db:
    await db.execute("SELECT * FROM users")
```

---

## 九、项目结构

> **注意**：项目结构因团队而异，此部分仅作为参考。

```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/          # 数据模型
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/        # 业务逻辑
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── repositories/    # 数据访问
│   │   ├── __init__.py
│   │   └── user_repository.py
│   ├── api/             # API 路由
│   │   ├── __init__.py
│   │   └── routes.py
│   └── utils/           # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── pyproject.toml
├── README.md
└── .env
```

---

## 十、测试规范

### 10.1 pytest 风格
```python
import pytest
from unittest.mock import Mock, patch

# PASS: 测试函数命名
def test_get_user_returns_user_when_found():
    # Arrange
    user_id = 1
    expected_user = User(id=user_id, name="John")
    
    # Act
    result = get_user(user_id)
    
    # Assert
    assert result == expected_user

# PASS: 参数化测试
@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("invalid-email", False),
    ("@example.com", False),
])
def test_validate_email(email: str, expected: bool):
    assert validate_email(email) == expected

# PASS: 异常测试
def test_get_user_raises_when_not_found():
    with pytest.raises(UserNotFoundError) as exc_info:
        get_user(999)
    assert exc_info.value.user_id == 999
```

### 10.2 Mock 使用
```python
from unittest.mock import AsyncMock, patch

# PASS: Mock 外部依赖
@patch("myproject.services.user_service.Database")
def test_create_user(mock_db_class):
    mock_db = Mock()
    mock_db_class.return_value = mock_db
    mock_db.execute.return_value = None
    
    service = UserService(mock_db)
    user = service.create_user(name="John", email="john@example.com")
    
    assert user.name == "John"
    mock_db.execute.assert_called_once()
```

---

## 十一、性能优化

### 11.1 常用优化
```python
# PASS: 使用 collections 模块
from collections import defaultdict, Counter, deque

# PASS: 使用生成器节省内存
large_list = [i for i in range(1000000)]  # 内存占用大
large_gen = (i for i in range(1000000))   # 内存友好

# PASS: 使用 lru_cache 缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n: int) -> int:
    return sum(i * i for i in range(n))
```

### 11.2 数据结构选择
```python
# 查找操作：set > list
if item in large_set:    # O(1)
    pass

if item in large_list:   # O(n)
    pass

# 频繁插入/删除：deque > list
queue = deque()
queue.append(item)       # O(1)
queue.popleft()          # O(1)

# 计数：Counter
word_count = Counter(words)
most_common = word_count.most_common(10)
```

---

## 十二、代码坏味道

| 问题 | 解决方案 |
|------|----------|
| 函数过长 | 拆分为更小函数 |
| 参数过多 | 使用 dataclass 或字典 |
| 魔法数字 | 使用命名常量 |
| 重复代码 | 提取公共函数/类 |
| 深度嵌套 | 使用早返回、卫语句 |
| 过度注释 | 让代码自解释 |
| 未使用导入 | 定期清理 |

---

## 十三、代码审查清单

- [ ] 类型注解完整
- [ ] 命名符合规范
- [ ] 函数职责单一
- [ ] 异常处理完善
- [ ] 测试覆盖关键场景
- [ ] 无循环导入
- [ ] 无未使用导入
- [ ] 代码格式一致（Black）

---

**记住**：Python 之禅：优美胜于丑陋，明确胜于隐式，简单胜于复杂。

*基于：PEP 8 + PEP 484 + Modern Python Best Practices*
