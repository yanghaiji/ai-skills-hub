# Go 编码规范

适用于 Go 1.21+ 的现代 Go 开发标准。

## 目录结构

```
golang-standards/
├── SKILL.md           # 完整规范文档
└── README.md          # 本文件
```

## 核心规范模块

| 模块 | 描述 |
|------|------|
| 代码风格 | gofmt、命名规范、缩写处理 |
| 项目结构 | cmd/internal/pkg 布局 |
| 类型设计 | 结构体、接口、类型断言 |
| 错误处理 | 自定义错误、错误包装、errors.Is/As |
| 并发模式 | goroutine、channel、select、context |
| 函数设计 | 选项模式、函数签名 |
| 包设计 | 依赖注入、API 设计 |
| 测试规范 | 表驱动测试、Mock、基准测试 |

## 使用方式

```
请按照 Go 编码规范编写以下代码：[需求描述]
```

## 关键速查

```go
// 错误处理
if err != nil {
    return fmt.Errorf("context: %w", err)
}

// 并发
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// 表驱动测试
tests := []struct {
    name string
    input int
    expected int
}{...}
```

*基于：Effective Go + Go Code Review Comments*
