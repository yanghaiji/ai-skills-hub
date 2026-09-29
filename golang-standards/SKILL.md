---
name: golang-standards
description: "Go 编码规范：项目结构、错误处理、并发模式、性能优化、测试。触发条件：编写Go代码、创建包、实现服务、代码审查时。"
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# Go 编码规范

适用于 Go 1.21+ 的现代 Go 开发标准。

## 何时激活

* 编写或审查 Go 代码时
* 创建包、模块或项目时
* 实现并发逻辑或微服务时
* **每次让AI编写Go代码时必须触发此规范**

## 核心原则

* 简洁性：Go 的哲学是少即是多
* 显式错误处理：错误是值，必须显式处理
* 并发原语：使用 goroutine 和 channel 而非锁
* 组合优于继承：使用接口和组合
* 可读性：代码是写给人看的

---

## 一、代码风格

### 1.1 格式化
- 使用 `gofmt` 或 `goimports` 格式化代码
- 行宽无限制，但建议保持在 100 字符以内
- 使用 Tab 缩进（gofmt 默认）

### 1.2 命名规范
```go
// PASS
type UserService struct {}    // 类型：PascalCase
func (s *UserService) GetUser() {} // 方法：PascalCase（导出）

func newUserService() *UserService {} // 函数：camelCase（未导出）

const MaxRetryCount = 3       // 常量：PascalCase 或 camelCase
var DefaultTimeout = 30 * time.Second // 变量：PascalCase 或 camelCase

// FAIL
type user_service struct {}   // 错误：蛇形命名
func Get_User() {}            // 错误：下划线
```

### 1.3 缩写与首字母缩写
```go
// PASS: 缩写保持一致
func (s *UserService) GetID() string {}    // ID 保持大写
func (s *UserService) GetURL() string {}   // URL 保持大写
func (s *UserService) GetHTTPClient() {}   // HTTP 保持大写

// 单个字母的变量
for i, v := range items {
    fmt.Println(i, v)
}
```

---

## 二、项目结构

> **注意**：项目结构因团队而异，此部分仅作为参考。

### 2.1 标准布局
```
project/
├── cmd/                    # 入口点
│   └── server/
│       └── main.go
├── internal/               # 私有代码
│   ├── handler/            # HTTP 处理器
│   ├── service/            # 业务逻辑
│   ├── repository/         # 数据访问
│   ├── model/              # 数据模型
│   └── config/             # 配置
├── pkg/                    # 公共库
│   └── logger/
├── api/                    # API 定义
│   └── proto/
├── go.mod
├── go.sum
└── README.md
```

### 2.2 Package 设计
```go
// PASS: 包名小写、简短、有意义
package user

// PASS: 文件名小写、下划线分隔
// user_service.go
// user_repository.go

// FAIL: 包名过长
package user_service_package
```

---

## 三、类型设计

### 3.1 结构体
```go
// PASS: 结构体定义
type User struct {
    ID        int64     `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

// PASS: 使用指针接收者修改结构体
func (u *User) SetName(name string) {
    u.Name = name
}

// PASS: 使用值接收者读取结构体
func (u User) FullName() string {
    return u.Name
}
```

### 3.2 接口
```go
// PASS: 接口小而精
type Reader interface {
    Read(p []byte) (n int, err error)
}

type UserRepository interface {
    GetByID(ctx context.Context, id int64) (*User, error)
    Create(ctx context.Context, user *User) error
}

// PASS: 在使用侧定义接口
type UserService struct {
    repo UserRepository  // 依赖注入
}

// FAIL: 在实现侧定义接口
type UserRepositoryImpl struct {} // 不好：接口应该在消费者侧
```

### 3.3 类型断言与类型 switch
```go
// PASS: 类型断言
func processValue(v interface{}) {
    if str, ok := v.(string); ok {
        fmt.Println("String:", str)
    }
}

// PASS: 类型 switch
func describe(i interface{}) {
    switch i.(type) {
    case string:
        fmt.Println("String")
    case int:
        fmt.Println("Int")
    default:
        fmt.Println("Unknown")
    }
}
```

---

## 四、错误处理

### 4.1 错误定义
```go
// PASS: 自定义错误类型
type NotFoundError struct {
    Resource string
    ID       int64
}

func (e *NotFoundError) Error() string {
    return fmt.Sprintf("%s with ID %d not found", e.Resource, e.ID)
}

// PASS: 使用 errors 包
import "errors"

var (
    ErrNotFound = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)
```

### 4.2 错误处理模式
```go
// PASS: 显式错误处理
func GetUser(id int64) (*User, error) {
    user, err := db.Query("SELECT * FROM users WHERE id = ?", id)
    if err != nil {
        return nil, fmt.Errorf("query user: %w", err)
    }
    return user, nil
}

// PASS: 使用 errors.Is 和 errors.As
if errors.Is(err, ErrNotFound) {
    // 处理未找到错误
}

var notFoundErr *NotFoundError
if errors.As(err, &notFoundErr) {
    fmt.Println(notFoundErr.Resource)
}
```

### 4.3 错误包装
```go
// PASS: 提供上下文信息
func (s *UserService) GetUser(ctx context.Context, id int64) (*User, error) {
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("get user by id %d: %w", id, err)
    }
    return user, nil
}

// PASS: 使用 %w 包装错误链
if err := doSomething(); err != nil {
    return fmt.Errorf("do something failed: %w", err)
}
```

### 4.4 错误使用禁忌
```go
// FAIL: 忽略错误
result, _ := doSomething()

// FAIL: 使用 panic 处理业务错误
if err != nil {
    panic(err)
}

// PASS: panic 仅用于不可恢复错误
if config == nil {
    panic("config is required")
}
```

---

## 五、并发模式

### 5.1 Goroutine
```go
// PASS: 启动 goroutine
go func() {
    defer wg.Done()
    processItem(item)
}()

// PASS: 使用 sync.WaitGroup
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        process(item)
    }(item)
}
wg.Wait()
```

### 5.2 Channel
```go
// PASS: 使用 channel 进行通信
func producer(ch chan<- int) {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    close(ch)
}

func consumer(ch <-chan int) {
    for v := range ch {
        fmt.Println(v)
    }
}

// PASS: 使用带缓冲的 channel
ch := make(chan int, 100)
```

### 5.3 Select 多路复用
```go
// PASS: 使用 select 处理多个 channel
select {
case msg := <-ch1:
    handle(msg)
case msg := <-ch2:
    handle(msg)
case <-time.After(5 * time.Second):
    fmt.Println("timeout")
case <-ctx.Done():
    fmt.Println("context cancelled")
}
```

### 5.4 Context 使用
```go
// PASS: 传递 context
func (s *UserService) GetUser(ctx context.Context, id int64) (*User, error) {
    // 检查 context
    select {
    case <-ctx.Done():
        return nil, ctx.Err()
    default:
    }
    
    // 使用 context
    return s.repo.GetByID(ctx, id)
}

// PASS: 创建超时 context
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

result, err := doSomething(ctx)
```

### 5.5 Sync 原语
```go
// PASS: 使用 sync.Mutex 保护共享状态
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

// PASS: 使用 sync.Once 确保单次执行
var once sync.Once

func initDatabase() {
    once.Do(func() {
        // 初始化数据库
    })
}
```

---

## 六、函数设计

### 6.1 函数签名
```go
// PASS: 返回值在前，错误在后
func GetUser(id int64) (*User, error) {}

// PASS: 使用选项模式
type Option func(*Service)

func WithTimeout(timeout time.Duration) Option {
    return func(s *Service) {
        s.timeout = timeout
    }
}

func NewService(opts ...Option) *Service {
    s := &Service{}
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// PASS: 使用 functional options
func NewServer(addr string, opts ...ServerOption) *Server {
    s := &Server{addr: addr}
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

### 6.2 函数长度
```go
// PASS: 短小函数
func validateEmail(email string) bool {
    return strings.Contains(email, "@")
}

// PASS: 提取辅助函数
func processOrder(order *Order) error {
    if err := validateOrder(order); err != nil {
        return err
    }
    if err := calculateTotal(order); err != nil {
        return err
    }
    return saveOrder(order)
}
```

---

## 七、包设计

### 7.1 包 API 设计
```go
// PASS: 导出函数和类型
package user

// UserService 提供用户相关操作
type UserService struct {
    repo Repository
}

// GetUser 根据 ID 获取用户
func (s *UserService) GetUser(ctx context.Context, id int64) (*User, error) {
    return s.repo.GetByID(ctx, id)
}

// 未导出函数不暴露实现细节
func hashPassword(password string) string {
    // 内部实现
}
```

### 7.2 包依赖
```go
// PASS: 依赖注入
type UserService struct {
    repo     UserRepository
    logger   Logger
    cache    Cache
}

func NewUserService(repo UserRepository, logger Logger, cache Cache) *UserService {
    return &UserService{
        repo:   repo,
        logger: logger,
        cache:  cache,
    }
}

// FAIL: 包内直接创建依赖
type UserService struct {
    repo *MySQLUserRepository // 硬编码具体实现
}
```

---

## 八、测试规范

### 8.1 表驱动测试
```go
// PASS: 表驱动测试
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.expected)
            }
        })
    }
}
```

### 8.2 Mock 与接口
```go
// PASS: 使用接口进行 Mock
type UserRepository interface {
    GetByID(ctx context.Context, id int64) (*User, error)
}

type mockUserRepository struct {
    users map[int64]*User
}

func (m *mockUserRepository) GetByID(ctx context.Context, id int64) (*User, error) {
    if user, ok := m.users[id]; ok {
        return user, nil
    }
    return nil, ErrNotFound
}

// PASS: 测试函数
func TestUserService_GetUser(t *testing.T) {
    repo := &mockUserRepository{
        users: map[int64]*User{
            1: {ID: 1, Name: "John"},
        },
    }
    
    service := NewUserService(repo, nil, nil)
    user, err := service.GetUser(context.Background(), 1)
    
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    
    if user.Name != "John" {
        t.Errorf("got name %s, want John", user.Name)
    }
}
```

### 8.3 基准测试
```go
// PASS: 基准测试
func BenchmarkSort(b *testing.B) {
    data := generateData(1000)
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        sort.Ints(data)
    }
}
```

---

## 九、性能优化

### 9.1 内存分配
```go
// PASS: 使用 sync.Pool 复用对象
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func process() {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer bufferPool.Put(buf)
    
    buf.Reset()
    // 使用 buffer
}

// PASS: 预分配 slice
items := make([]Item, 0, len(input)) // 预分配容量
```

### 9.2 字符串优化
```go
// PASS: 使用 strings.Builder
var builder strings.Builder
for i := 0; i < 1000; i++ {
    builder.WriteString("a")
}
result := builder.String()

// PASS: 使用 []byte 进行字符串操作
func toUpper(s string) string {
    b := make([]byte, len(s))
    copy(b, s)
    for i := range b {
        if b[i] >= 'a' && b[i] <= 'z' {
            b[i] -= 32
        }
    }
    return string(b)
}
```

### 9.3 并发优化
```go
// PASS: 使用 worker pool
func processItems(items []Item) []Result {
    results := make([]Result, len(items))
    ch := make(chan int, len(items))
    
    // 启动 worker
    var wg sync.WaitGroup
    for i := 0; i < runtime.NumCPU(); i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for idx := range ch {
                results[idx] = process(items[idx])
            }
        }()
    }
    
    // 发送任务
    for i := range items {
        ch <- i
    }
    close(ch)
    
    wg.Wait()
    return results
}
```

---

## 十、代码坏味道

| 问题 | 解决方案 |
|------|----------|
| 错误被忽略 | 始终检查错误 |
| 函数过长 | 提取辅助函数 |
| 接口过大 | 拆分为小接口 |
| 深度嵌套 | 使用卫语句、早返回 |
| 魔法数字 | 使用命名常量 |
| 硬编码 | 使用配置、依赖注入 |
| 未使用代码 | 定期清理 |

---

## 十一、代码审查清单

- [ ] 使用 `gofmt` 格式化
- [ ] 命名符合规范（导出 PascalCase，未导出 camelCase）
- [ ] 错误显式处理
- [ ] Context 正确传递
- [ ] 无数据竞争
- [ ] 无资源泄漏（defer close）
- [ ] 接口小而精
- [ ] 测试覆盖关键路径

---

**记住**：Go 的哲学：少即是多，显式优于隐式，组合优于继承。

*基于：Effective Go + Go Code Review Comments*
