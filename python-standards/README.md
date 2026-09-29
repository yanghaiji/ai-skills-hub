# Python 编码规范

适用于 Python 3.10+ 的现代 Python 开发标准。

## 目录结构

```
python-standards/
├── SKILL.md           # 完整规范文档
└── README.md          # 本文件
```

## 核心规范模块

| 模块 | 描述 |
|------|------|
| 代码风格 | PEP 8、命名规范、导入顺序 |
| 类型注解 | 函数签名、变量注解、Protocol |
| 数据类 | dataclass、Pydantic、枚举 |
| 函数设计 | 参数设计、返回值、短小函数 |
| 异常处理 | 自定义异常、上下文管理器 |
| 类设计 | 成员顺序、魔术方法 |
| 迭代器 | 生成器、迭代器协议 |
| 异步编程 | async/await、异步上下文管理器 |
| 测试规范 | pytest、参数化、Mock |

## 使用方式

```
请按照 Python 编码规范编写以下代码：[需求描述]
```

## 关键速查

```python
# 类型注解
def get_user(user_id: int) -> Optional[User]: ...

# 数据类
@dataclass
class User:
    id: int
    name: str

# 异常处理
try:
    result = do_something()
except SpecificError as e:
    logger.error(f"Error: {e}")
    raise
```

*基于：PEP 8 + PEP 484 + Modern Python Best Practices*
