# 常见设计模式参考

## 创建型模式

### 单例模式 (Singleton)
确保一个类只有一个实例，并提供全局访问点。

```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 工厂模式 (Factory)
定义一个创建对象的接口，让子类决定实例化哪个类。

```python
class Factory:
    def create(self, product_type):
        if product_type == "A":
            return ProductA()
        elif product_type == "B":
            return ProductB()
        raise ValueError(f"Unknown product type: {product_type}")
```

### 建造者模式 (Builder)
将复杂对象的构建与其表示分离。

```python
class Builder:
    def __init__(self):
        self.product = Product()
    
    def set_name(self, name):
        self.product.name = name
        return self
    
    def set_price(self, price):
        self.product.price = price
        return self
    
    def build(self):
        return self.product
```

## 结构型模式

### 适配器模式 (Adapter)
将一个类的接口转换成客户期望的另一个接口。

```python
class Adapter:
    def __init__(self, adaptee):
        self.adaptee = adaptee
    
    def new_method(self):
        return self.adaptee.old_method()
```

### 装饰器模式 (Decorator)
动态地给对象添加职责。

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@decorator
def my_function():
    pass
```

### 代理模式 (Proxy)
为其他对象提供一种代理以控制对这个对象的访问。

```python
class Proxy:
    def __init__(self, real_subject):
        self._real_subject = real_subject
    
    def request(self):
        if self.check_access():
            self._real_subject.request()
    
    def check_access(self):
        # 访问控制逻辑
        return True
```

## 行为型模式

### 观察者模式 (Observer)
定义对象间的一种一对多的依赖关系。

```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)
```

### 策略模式 (Strategy)
定义一系列算法，使它们可互相替换。

```python
class Strategy:
    def execute(self, data):
        raise NotImplementedError

class ConcreteStrategyA(Strategy):
    def execute(self, data):
        return sorted(data)

class ConcreteStrategyB(Strategy):
    def execute(self, data):
        return reversed(sorted(data))

class Context:
    def __init__(self, strategy):
        self._strategy = strategy
    
    def do_something(self, data):
        return self._strategy.execute(data)
```

### 状态模式 (State)
允许对象在内部状态改变时改变它的行为。

```python
class State:
    def handle(self, context):
        raise NotImplementedError

class ConcreteStateA(State):
    def handle(self, context):
        context.state = ConcreteStateB()

class ConcreteStateB(State):
    def handle(self, context):
        context.state = ConcreteStateA()

class Context:
    def __init__(self):
        self._state = ConcreteStateA()
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, state):
        self._state = state
    
    def request(self):
        self._state.handle(self)
```

## 常见架构模式

### MVC (Model-View-Controller)
- **Model**: 数据和业务逻辑
- **View**: 用户界面
- **Controller**: 处理用户输入，协调Model和View

### MVVM (Model-View-ViewModel)
- **Model**: 数据层
- **View**: 视图层
- **ViewModel**: 视图模型，处理视图逻辑

### 分层架构
```
┌─────────────────────────────┐
│      表示层 (UI/Presentation)│
├─────────────────────────────┤
│      业务逻辑层 (Business)    │
├─────────────────────────────┤
│      数据访问层 (Data Access)  │
├─────────────────────────────┤
│      数据库/外部服务           │
└─────────────────────────────┘
```

### 微服务架构
- 服务拆分
- API网关
- 服务发现
- 配置中心

## SOLID原则

| 原则 | 说明 |
|------|------|
| **S** - 单一职责 | 一个类只负责一件事 |
| **O** - 开闭原则 | 对扩展开放，对修改关闭 |
| **L** - 里氏替换 | 子类可以替换父类 |
| **I** - 接口隔离 | 不强迫依赖不需要的接口 |
| **D** - 依赖倒置 | 依赖抽象而非具体实现 |

## DRY / KISS / YAGNI

- **DRY** (Don't Repeat Yourself): 避免重复代码
- **KISS** (Keep It Simple, Stupid): 保持简单
- **YAGNI** (You Aren't Gonna Need It): 不需要就不做

---

*选择设计模式时，优先考虑简单性和可维护性，不要过度设计。*
