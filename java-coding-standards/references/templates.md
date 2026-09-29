# 常用代码模板

> 本文件包含 Spring Boot 项目中常用的标准代码模板，配合 `java-coding-standards` Skill 使用。

## 标准 Controller

```java
@RestController
@RequestMapping("/api/v1")
@Slf4j
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping("/user/{id}")
    public ResponseDTO<UserDTO> getUser(@PathVariable Long id) {
        return ResponseDTO.success(userService.getUser(id));
    }
}
```

## 标准 Service

```java
@Service
@Slf4j
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserMapper userMapper;

    @Override
    public UserDTO getUser(Long id) {
        User user = userMapper.selectById(id);
        return BeanUtil.copyProperties(user, UserDTO.class);
    }
}
```

## 标准 DTO（Record）

```java
public record UserDTO(Long id, String name, String email) {}
```

## 标准异常类

```java
public class BusinessException extends RuntimeException {
    private final String errorCode;

    public BusinessException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public String getErrorCode() {
        return errorCode;
    }
}
```

## 标准全局异常处理

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseDTO<?> handleBusiness(BusinessException e) {
        log.warn("business_error code={} msg={}", e.getErrorCode(), e.getMessage());
        return ResponseDTO.fail(e.getErrorCode(), e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    public ResponseDTO<?> handleException(Exception e) {
        log.error("system_error", e);
        return ResponseDTO.fail("B0001", "系统内部错误");
    }
}
```
