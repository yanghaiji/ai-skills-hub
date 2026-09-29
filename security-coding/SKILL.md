---
name: security-coding
description: "安全编码规范：OWASP Top 10、输入校验、认证授权、数据保护。触发条件：编写涉及安全的代码时。"
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# 安全编码规范

基于 OWASP Top 10 的现代应用安全编码标准。

## 何时激活

* 编写用户输入处理代码时
* 实现认证授权功能时
* 处理敏感数据时
* **每次让AI编写安全相关代码时必须触发此规范**

---

## 一、注入防护

### 1.1 SQL 注入
```java
// ❌ 字符串拼接
String sql = "SELECT * FROM user WHERE name = '" + name + "'";

// ✅ 参数化查询
String sql = "SELECT * FROM user WHERE name = ?";
PreparedStatement ps = conn.prepareStatement(sql);
ps.setString(1, name);

// ✅ JPA/MyBatis
@Query("SELECT u FROM User u WHERE u.name = :name")
User findByName(@Param("name") String name);
```

### 1.2 XSS 防护
```java
// ❌ 直接输出
response.getWriter().write(userInput);

// ✅ 转义输出
String safe = HtmlUtils.htmlEscape(userInput);
response.getWriter().write(safe);

// ✅ 前端转义
// React 默认转义
// Vue v-text 而非 v-html
```

### 1.3 命令注入
```java
// ❌ 执行系统命令
Runtime.getRuntime().exec("ping " + userInput);

// ✅ 使用白名单
List<String> allowedHosts = List.of("host1.com", "host2.com");
if (!allowedHosts.contains(userInput)) {
    throw new SecurityException("非法主机");
}
```

---

## 二、认证安全

### 2.1 密码存储
```java
// ❌ 明文存储
String password = "123456";
user.setPassword(password);

// ✅ BCrypt 加密
String hashed = BCrypt.hashpw(password, BCrypt.gensalt(12));
user.setPassword(hashed);

// ✅ 验证密码
boolean match = BCrypt.checkpw(inputPassword, storedHash);
```

### 2.2 Token 安全
```java
// ✅ JWT 最佳实践
String token = Jwts.builder()
    .setSubject(userId)
    .setIssuedAt(new Date())
    .setExpiration(new Date(System.currentTimeMillis() + 3600000))
    .signWith(SignatureAlgorithm.HS256, secretKey)
    .compact();

// ✅ Token 验证
try {
    Claims claims = Jwts.parser()
        .setSigningKey(secretKey)
        .parseClaimsJws(token)
        .getBody();
} catch (ExpiredJwtException e) {
    // Token 过期
} catch (SignatureException e) {
    // Token 无效
}
```

### 2.3 登录安全
```java
// ✅ 登录限制
if (loginAttempts >= 5) {
    throw new TooManyAttemptsException("登录次数过多，请15分钟后重试");
}

// ✅ 登录日志
log.info("登录成功: userId={}, ip={}", userId, ip);
log.warn("登录失败: username={}, ip={}", username, ip);
```

---

## 三、授权控制

### 3.1 权限校验
```java
// ✅ 方法级别权限
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser(Long userId) { }

// ✅ 数据级别权限
public Order getOrder(Long orderId) {
    Order order = orderRepository.findById(orderId);
    if (!order.getUserId().equals(currentUserId)) {
        throw new AccessDeniedException("无权访问");
    }
    return order;
}
```

### 3.2 最小权限原则
```java
// ✅ 只授予必要权限
@Secured("ROLE_READ_ONLY")
public List<User> getUsers() { }

// ❌ 过度权限
@Secured("ROLE_ADMIN")
public List<User> getUsers() { }
```

---

## 四、数据保护

### 4.1 敏感数据加密
```java
// ✅ AES 加密
public String encrypt(String data, String key) {
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key.getBytes(), "AES"));
    return Base64.getEncoder().encodeToString(cipher.doFinal(data.getBytes()));
}

// ✅ 敏感字段加密存储
@Entity
public class User {
    @Column(columnDefinition = "VARBINARY(256)")
    @Convert(converter = EncryptionConverter.class)
    private String idCard;
}
```

### 4.2 日志脱敏
```java
// ❌ 日志泄露
log.info("用户信息: {}", user);
log.info("手机号: {}", phone);

// ✅ 日志脱敏
log.info("用户信息: {}", user.withMaskedSensitiveData());
log.info("手机号: {}", maskPhone(phone));

private String maskPhone(String phone) {
    if (phone == null || phone.length() < 7) return phone;
    return phone.substring(0, 3) + "****" + phone.substring(7);
}
```

### 4.3 响应脱敏
```java
// ✅ DTO 脱敏
public class UserDTO {
    private Long id;
    private String name;
    
    @JsonSerialize(using = MaskingSerializer.class)
    private String phone;  // 138****1234
    
    @JsonSerialize(using = MaskingSerializer.class)
    private String email;  // j***@test.com
}
```

---

## 五、输入校验

### 5.1 参数校验
```java
// ✅ 使用 Bean Validation
public class CreateUserRequest {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 50)
    private String name;
    
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;
    
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;
}

// ✅ 方法级别校验
@Validated
public interface ValidationGroups {
    interface Create {}
    interface Update {}
}
```

### 5.2 文件上传
```java
// ✅ 文件类型校验
private static final Set<String> ALLOWED_TYPES = Set.of(
    "image/jpeg", "image/png", "application/pdf"
);

public void uploadFile(MultipartFile file) {
    if (!ALLOWED_TYPES.contains(file.getContentType())) {
        throw new IllegalArgumentException("不支持的文件类型");
    }
    
    // ✅ 文件大小限制
    if (file.getSize() > 10 * 1024 * 1024) {  // 10MB
        throw new IllegalArgumentException("文件过大");
    }
    
    // ✅ 文件名消毒
    String filename = StringUtils.cleanPath(file.getOriginalFilename());
    if (filename.contains("..")) {
        throw new IllegalArgumentException("非法文件名");
    }
}
```

---

## 六、API 安全

### 6.1 HTTPS
```java
// ✅ 强制 HTTPS
@Bean
public ServletWebServerFactory servletContainer() {
    TomcatServletWebServerFactory tomcat = new TomcatServletWebServerFactory();
    tomcat.addAdditionalTomcatConnectors(httpRedirectConnector());
    return tomcat;
}

private Connector httpRedirectConnector() {
    Connector connector = new Connector(TomcatServletWebServerFactory.DEFAULT_PROTOCOL);
    connector.setScheme("http");
    connector.setPort(8080);
    connector.setSecure(false);
    connector.setRedirectPort(443);
    return connector;
}
```

### 6.2 CORS 配置
```java
// ✅ 限制 CORS 来源
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://myapp.com")  // 不要用 *
            .allowedMethods("GET", "POST", "PUT", "DELETE")
            .allowedHeaders("*")
            .allowCredentials(true)
            .maxAge(3600);
    }
}
```

### 6.3 速率限制
```java
// ✅ 接口限流
@RateLimiter(name = "apiLimiter", fallbackMethod = "fallback")
@GetMapping("/api/data")
public Data getData() { }

public Data fallback() {
    throw new TooManyRequestsException("请求过于频繁");
}
```

---

## 七、常见漏洞速查

| 漏洞 | 防护措施 |
|------|----------|
| SQL 注入 | 参数化查询 |
| XSS | 输出转义、CSP |
| CSRF | Token 验证 |
| XXE | 禁用外部实体 |
| 反序列化 | 白名单校验 |
| SSRF | URL 白名单 |
| 文件上传 | 类型/大小校验 |
| 敏感信息泄露 | 脱敏、加密 |

---

## 代码审查清单

- [ ] SQL 使用参数化查询
- [ ] 用户输入已校验
- [ ] 密码已加密存储
- [ ] 日志已脱敏
- [ ] 敏感数据已加密
- [ ] 权限已校验
- [ ] HTTPS 已启用
- [ ] CORS 已限制

---

*参考：OWASP Top 10 2021 + CWE/SANS Top 25*
