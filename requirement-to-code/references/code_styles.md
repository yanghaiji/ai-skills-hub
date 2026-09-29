# 代码风格参考

## Python

### 缩进
- 使用 4 个空格进行缩进
- 不要使用 Tab

### 引号
- 字符串优先使用单引号 `'`
- 文档字符串使用三引号 `'''` 或 `"""`

### 命名规范
- 文件名: `snake_case.py`
- 类名: `PascalCase`
- 函数名: `snake_case`
- 变量名: `snake_case`
- 常量: `UPPER_SNAKE_CASE`
- 私有成员: `_leading_underscore`

### 导入顺序
```python
# 标准库
import os
import sys
from pathlib import Path

# 第三方库
import requests
from flask import Flask

# 本地模块
from .local_module import LocalClass
```

### 注释
```python
# 单行注释

"""
多行注释/文档字符串
"""

def my_function():
    """函数文档字符串"""
    pass
```

## JavaScript/TypeScript

### 缩进
- 使用 2 个空格进行缩进

### 引号
- 字符串优先使用单引号 `'`
- JSX 属性使用双引号 `"`

### 命名规范
- 文件名: `kebab-case.js` 或 `PascalCase.js`（组件）
- 类名: `PascalCase`
- 函数名: `camelCase`
- 变量名: `camelCase`
- 常量: `UPPER_SNAKE_CASE`
- 私有成员: `#privateField`

### 导入顺序
```javascript
// 第三方库
import React from 'react';
import axios from 'axios';

// 本地模块
import { Component } from './Component';
import styles from './styles.module.css';
```

## Java

### 缩进
- 使用 4 个空格进行缩进

### 命名规范
- 文件名: `PascalCase.java`
- 类名: `PascalCase`
- 方法名: `camelCase`
- 变量名: `camelCase`
- 常量: `UPPER_SNAKE_CASE`

### 注释
```java
/**
 * 类/方法文档注释
 */
public class MyClass {
    // 单行注释
    
    /**
     * 方法文档注释
     */
    public void myMethod() {
        // 方法实现
    }
}
```

## Go

### 缩进
- 使用 Tab 进行缩进

### 命名规范
- 文件名: `snake_case.go`
- 结构体/接口: `PascalCase`
- 函数/方法: `PascalCase`（导出）/ `camelCase`（未导出）
- 变量: `camelCase`
- 常量: `PascalCase` 或 `UPPER_SNAKE_CASE`

### 注释
```go
// 单行注释

/*
多行注释
*/

// FunctionName 函数文档注释
func FunctionName() {
    // 函数实现
}
```

## 通用原则

1. **一致性**: 保持与项目现有代码风格一致
2. **可读性**: 代码应该易于阅读和理解
3. **简洁性**: 避免不必要的复杂性
4. **注释**: 只在必要时添加注释，解释"为什么"而不是"做什么"
