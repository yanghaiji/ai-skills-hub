---
name: api-design
description: "RESTful API 设计规范：URL 设计、HTTP 方法、状态码、版本控制、错误处理。触发条件：设计API、编写接口文档时。"
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# RESTful API 设计规范

适用于现代微服务和前后端分离架构的 API 设计标准。

## 何时激活

* 设计新的 API 接口时
* 编写接口文档时
* **每次让AI设计API时必须触发此规范**

---

## 一、URL 设计

### 1.1 资源命名（复数名词）
```
# ✅ 正确
GET    /api/v1/users
GET    /api/v1/users/123
POST   /api/v1/users
PUT    /api/v1/users/123
DELETE /api/v1/users/123

# ❌ 错误
GET    /api/v1/getUser
POST   /api/v1/createUser
```

### 1.2 URL 结构
```
https://api.example.com/v1/users/123/orders/456
         ↑         ↑    ↑    ↑      ↑    ↑
       域名      版本  资源  ID   子资源  ID
```

### 1.3 嵌套资源
```
# 用户的订单
GET /users/{userId}/orders

# 订单的商品
GET /orders/{orderId}/items

# 避免超过 3 层嵌套
GET /users/{userId}/orders/{orderId}/items/{itemId}  # 可接受
GET /users/{userId}/orders/{orderId}/items/{itemId}/reviews  # 过深
```

---

## 二、HTTP 方法

| 方法 | 用途 | 幂等 | 安全 |
|------|------|------|------|
| GET | 获取资源 | ✅ | ✅ |
| POST | 创建资源 | ❌ | ❌ |
| PUT | 全量更新 | ✅ | ❌ |
| PATCH | 部分更新 | ❌ | ❌ |
| DELETE | 删除资源 | ✅ | ❌ |

```bash
# GET - 查询
GET /api/v1/users
GET /api/v1/users/123
GET /api/v1/users?status=active&page=1&size=20

# POST - 创建
POST /api/v1/users
Body: { "name": "John", "email": "john@test.com" }

# PUT - 全量更新
PUT /api/v1/users/123
Body: { "name": "John", "email": "john@test.com", "phone": "13800138000" }

# PATCH - 部分更新
PATCH /api/v1/users/123
Body: { "phone": "13800138000" }

# DELETE - 删除
DELETE /api/v1/users/123
```

---

## 三、状态码

### 3.1 成功状态码
| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | OK | GET/PUT/PATCH 成功 |
| 201 | Created | POST 创建成功 |
| 204 | No Content | DELETE 成功 |

### 3.2 客户端错误
| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 400 | Bad Request | 参数校验失败 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 业务逻辑错误 |

### 3.3 服务端错误
| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务不可用 |

---

## 四、请求/响应

### 4.1 请求头
```http
Content-Type: application/json
Authorization: Bearer <token>
Accept: application/json
```

### 4.2 响应格式
```json
// 成功
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 123,
    "name": "John"
  }
}

// 列表
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "size": 20
  }
}

// 错误
{
  "code": 400,
  "message": "参数校验失败",
  "errors": [
    {"field": "email", "message": "邮箱格式不正确"}
  ]
}
```

---

## 五、查询参数

### 5.1 分页
```
GET /api/v1/users?page=1&size=20
GET /api/v1/users?offset=0&limit=20
```

### 5.2 过滤
```
GET /api/v1/users?status=active
GET /api/v1/users?role=admin&is_vip=true
```

### 5.3 排序
```
GET /api/v1/users?sort=created_at:desc
GET /api/v1/users?sort=-created_at,name
```

### 5.4 字段选择
```
GET /api/v1/users?fields=id,name,email
```

---

## 六、版本控制

### 6.1 URL 版本
```
/api/v1/users
/api/v2/users
```

### 6.2 Header 版本
```http
Accept: application/vnd.myapp.v1+json
```

---

## 七、认证与安全

### 7.1 Token 认证
```http
Authorization: Bearer <jwt-token>
```

### 7.2 API Key
```http
X-API-Key: <api-key>
```

### 7.3 速率限制
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## 代码审查清单

- [ ] URL 使用复数名词
- [ ] HTTP 方法正确
- [ ] 状态码准确
- [ ] 响应格式统一
- [ ] 错误信息清晰
- [ ] 敏感数据已脱敏
- [ ] 已考虑分页

---

*参考：RESTful API Design Best Practices + Microsoft/Google API Guidelines*
