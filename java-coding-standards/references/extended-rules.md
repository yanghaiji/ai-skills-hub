# 扩展规约

> 本文件包含 `java-coding-standards` Skill 的扩展规约，涵盖控制语句、注释、安全和数据库相关内容。
> 核心规约请在主 SKILL.md 中查阅，本文件作为补充参考。

---

## 一、控制语句

### 1.1 switch 规范
- 每个 case 必须有 break / return / continue，否则注释说明
- 必须有 default 且放在最后
- String 类型变量为外部参数时，必须先做 null 判断

### 1.2 if/else 规范
```java
// PASS: 卫语句，提前返回
if (man.isUgly()) { return; }
if (man.isPoor()) { return; }
// 正常业务逻辑
```
- if / else / for / while / do 必须使用大括号
- 超过 3 层的 if-else 用卫语句、策略模式、状态模式替代
- 不要在条件判断中执行复杂语句，赋值给有意义的布尔变量

### 1.3 高并发注意
- 高并发场景避免"等于"判断作为中断条件，用区间判断（防止击穿）

### 1.4 三目运算符 NPE
```java
// FAIL: 自动拆箱导致 NPE
Integer a = 1, b = 2, c = null;
Boolean flag = false;
Integer result = (flag ? a * b : c); // c 为 null，拆箱 NPE
```

### 1.5 性能
- 循环体内对象定义、变量获取、不必要的 try-catch 尽量移到循环外
- 公开接口必须做入参保护，尤其是批量操作

---

## 二、注释规约

### 2.1 Javadoc
- 类、类属性、类方法注释必须用 `/** */` 格式
- 所有抽象方法必须用 Javadoc 注释
- 所有类必须添加 `@author` 和 `@date`

### 2.2 行内注释
- 方法内单行注释用 `//`，放在被注释语句上方
- 方法内多行注释用 `/* */`
- 所有枚举类型字段必须有注释

### 2.3 维护
- 代码修改时注释同步修改
- 删除未使用的字段、方法、参数
- 谨慎注释掉代码，无用代码直接删除
- TODO / FIXME 标记需注明人与时间

---

## 三、安全规约

### 3.1 权限与数据
- 用户个人页面/功能必须进行权限校验
- 用户敏感数据必须脱敏展示
- SQL 参数严格使用参数绑定，禁止字符串拼接 SQL

### 3.2 输入验证
- 用户请求传入的任何参数必须做有效性验证
- 防范：页面 size 过大、恶意 order by、缓存击穿、SSRF、SQL 注入、ReDoS

### 3.3 Web 安全
- 禁止向 HTML 输出未经转义的用户数据（防 XSS）
- 表单 / AJAX 提交必须执行 CSRF 验证
- URL 外部重定向必须白名单过滤

### 3.4 资源保护
- 短信/邮件/支付等必须防重放（数量限制、验证码）
- 文件上传必须检查大小和类型
- 配置文件中的密码需要加密

---

## 五、测试期望

```java
// PASS: JUnit 5 + AssertJ
@Test
void shouldFindMarketBySlug() {
    Market market = new Market(1L, "test", MarketStatus.ACTIVE);
    
    when(marketRepository.findBySlug("test"))
        .thenReturn(Optional.of(market));
    
    MarketDTO result = marketService.findBySlug("test");
    
    assertThat(result).isNotNull();
    assertThat(result.name()).isEqualTo("test");
}
```

- 使用 Mockito 进行模拟；尽可能避免部分模拟
- 倾向于确定性测试；没有隐藏的休眠

---

## 六、项目结构（参考）

> **注意**：项目结构因公司/团队而异，此部分仅作为参考，实际以团队规范为准。

```
src/main/java/com/example/app/
  config/          # 配置类
  controller/      # 控制层
  service/         # 业务层
  repository/      # 数据访问
  domain/          # 领域模型
  dto/             # 数据传输对象
  util/            # 工具类
  exception/       # 异常定义
  constant/        # 常量定义
src/main/resources/
  application.yml
src/test/java/... (mirrors main)
```
