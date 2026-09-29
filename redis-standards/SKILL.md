---
name: redis-standards
description: "Redis 使用规范：数据结构、缓存策略、键设计、性能优化、常见问题。触发条件：使用 Redis、设计缓存时。"
metadata:
  author: Yanghaiji
  version: "1.0.2"
---

# Redis 使用规范

适用于现代应用中 Redis 缓存的设计和使用标准。

## 何时激活

* 使用 Redis 进行缓存时
* 设计缓存策略时
* **每次让 AI 编写 Redis 相关代码时必须触发此规范**

---

## 一、键设计规范

### 1.1 命名格式
```
{业务模块}:{对象类型}:{ID}

示例：
user:1001
user:1001:profile
order:2024:1001
cache:user:1001
```

### 1.2 命名规则
```bash
# ✅ 正确
user:1001
order:20240101:1001
product:sku:12345

# ❌ 错误
User:1001          # 大写
user_1001          # 下划线
1001               # 无语义
```

### 1.3 长度限制
- 键名最长 512 字节
- 建议不超过 30 字符
- 避免过长的前缀

---

## 二、数据结构选择

| 场景 | 数据结构 | 命令 |
|------|----------|------|
| 简单缓存 | String | SET/GET |
| 对象缓存 | Hash | HSET/HGET |
| 列表数据 | List | LPUSH/LPOP |
| 去重集合 | Set | SADD/SMEMBERS |
| 排行榜 | Sorted Set | ZADD/ZRANGE |
| 计数器 | String | INCR/DECR |
| 位运算 | Bitmap | SETBIT |

```bash
# String - 简单缓存
SET user:1001 '{"name":"John"}'
GET user:1001

# Hash - 对象缓存
HSET user:1001 name "John" email "john@test.com"
HGET user:1001 name

# Sorted Set - 排行榜
ZADD leaderboard 100 "user:1001"
ZREVRANGE leaderboard 0 9 WITHSCORES
```

---

## 三、缓存策略

### 3.1 缓存模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| Cache Aside | 先查缓存，miss 则查库 | 通用 |
| Read Through | 缓存层自动加载 | 读多写少 |
| Write Behind | 异步写入数据库 | 高写入 |

### 3.2 过期时间
```bash
# ✅ 设置合理过期时间
SET user:1001 '{"name":"John"}' EX 3600  # 1 小时

# ✅ 热点数据长过期，普通数据短过期
SET config:site '{"theme":"dark"}' EX 86400  # 24 小时
SET session:abc123 '{"userId":1001}' EX 1800  # 30 分钟

# ❌ 不设置过期时间（除非永不过期的数据）
SET temp:data "value"
```

### 3.3 过期时间随机化（防雪崩）
```java
// ✅ 添加随机偏移
int baseTTL = 3600;
int randomOffset = ThreadLocalRandom.current().nextInt(300);
redis.setex(key, baseTTL + randomOffset, value);

// ❌ 固定过期时间（可能导致同时失效）
redis.setex(key, 3600, value);
```

---

## 四、常见问题防护

### 4.1 缓存穿透
```java
// 问题：查询不存在的数据，每次都打到数据库
// 解决：缓存空值
public User getUser(Long id) {
    String key = "user:" + id;
    String value = redis.get(key);
    
    if (value != null) {
        if (value.equals("NULL")) {
            return null;
        }
        return parseUser(value);
    }
    
    User user = db.getUser(id);
    if (user == null) {
        redis.setex(key, 300, "NULL");  // 缓存空值，短过期
    } else {
        redis.setex(key, 3600, toJson(user));
    }
    return user;
}
```

### 4.2 缓存击穿
```java
// 问题：热点 key 过期，大量请求打到数据库
// 解决：Redisson 分布式锁（推荐）或 Redis SETNX
public User getUser(Long id) {
    String key = "user:" + id;
    String value = redis.get(key);

    if (value != null) {
        return parseUser(value);
    }

    // ✅ 使用 Redisson 分布式锁（推荐）
    RLock lock = redissonClient.getLock("lock:" + key);
    boolean isLocked = false;
    try {
        isLocked = lock.tryLock(0, 10, TimeUnit.SECONDS);
        if (isLocked) {
            User user = db.getUser(id);
            if (user != null) {
                redis.setex(key, 3600, toJson(user));
            }
            return user;
        }
        return null;  // 未获锁，可短暂等待后重试
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        return null;
    } finally {
        if (isLocked && lock.isHeldByCurrentThread()) {
            lock.unlock();
        }
    }
}
```

> 💡 **提示**：Redisson 完整用法（可重入锁、看门狗、MultiLock、分布式对象）请参考 [Redisson 使用指南](references/redisson-guide.md)

### 4.3 缓存雪崩
```java
// 问题：大量 key 在同一时刻集中失效，或 Redis 服务整体宕机，
//      导致海量请求瞬间穿透到数据库，DB 压力骤增甚至崩堆
// 区别：雪崩是“大批 key”同时失效；击穿是“单个热点 key”失效

// 解决（多重防护叠加）：
// 1. 过期时间随机化，避免集中失效（见 §3.3）
// 2. 多级缓存：本地缓存(Caffeine) + Redis，Redis 挂了还有本地兜底
// 3. Redis 高可用：集群 + 哨兵/主从，避免单点宕机
// 4. 缓存预热：系统启动/大促前提前加载热点数据
// 5. 限流降级/熔断：Sentinel/Hystrix 保护 DB，避免被打垮

@Cacheable(cacheNames = "user")  // 一级：本地缓存
public User getUser(Long id) {
    String key = "user:" + id;
    String value = redis.get(key);          // 二级：Redis
    if (value != null) {
        return parseUser(value);
    }
    // Redis 也 miss（可能刚批量失效），用互斥锁限制回源并发，保护 DB
    return loadWithProtection(key, id);
}
```

---

## 五、性能优化

### 5.1 批量操作
```java
// ✅ 使用 Pipeline 批量查询
List<String> keys = Arrays.asList("user:1", "user:2", "user:3");
List<Object> values = redis.pipelined(p -> {
    keys.forEach(p::get);
    return null;
});

// ❌ 逐个查询
for (String key : keys) {
    redis.get(key);
}
```

### 5.2 大 Key 问题
```bash
# 查找大 Key
redis-cli --bigkeys

# 避免：
# 1. String 类型 value 超过 10KB
# 2. Hash/Set/ZSet 元素超过 5000
# 3. List 元素超过 10000

# 解决：拆分
user:1001:info    # 基本信息
user:1001:detail  # 详细信息
```

### 5.3 热 Key 处理
```java
// 1. 本地缓存 + Redis 缓存
@Cacheable(value = "user", key = "#id")
public User getUser(Long id) {
    return db.getUser(id);
}

// 2. Redis 集群读写分离
```

---

## 六、连接池配置

> **客户端选型：统一使用 Lettuce**（Spring Boot 2.x+ 默认）。Lettuce 基于 Netty 非阻塞 IO、连接线程安全、单连接可被多线程共享，性能和资源占用优于阻塞式的 Jedis。
> 仅当维护历史遗留项目才用 Jedis；
> **Redisson** 的连接池参数见 [Redisson 使用指南](references/redisson-guide.md)。

### 6.1 Lettuce 连接池（推荐，Spring Boot 默认）
```yaml
# application.yml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password: ${REDIS_PASSWORD:}
      database: 0
      timeout: 3000ms           # 命令执行超时
      connect-timeout: 3000ms   # 连接超时
      lettuce:
        pool:
          enabled: true
          max-active: 32    # 最大连接数（≈峰值 QPS × 平均耗时 ms / 1000，留 2 倍余量）
          max-idle: 16      # 最大空闲连接
          min-idle: 4       # 最小空闲连接（避免突发流量时建连开销）
          max-wait: 3000ms  # 获取连接最大等待时间（❌ 避免 -1 无限等待）
        shutdown-timeout: 200ms
```

### 6.2 参数设置原则
| 参数 | 建议值 | 说明 |
|------|--------|------|
| max-active | 业务线程数的 1~2 倍 | 过大增加 Redis 负担，过小导致获取连接阻塞 |
| max-idle | max-active 的 1/2 | 保持一定空闲连接复用 |
| min-idle | 高峰需求的 1/3 | 预热连接，避免突发流量建连延迟 |
| max-wait | 1~3 秒 | ❌ 禁止 -1（连接池耗尽时线程永久阻塞） |
| timeout | 略大于慢查询阈值 | 命令超时，单位毫秒 |

```bash
# Redis 服务端配套检查
maxclients 10000          # 服务端最大客户端数，需 ≥ 所有实例连接池 max-active 之和
client timeout 300        # 空闲客户端断开时间（秒），应小于连接池空闲回收周期
```

### 6.3 常见问题
```java
// ❌ 连接池耗尽 / 超时典型错误
RedisConnectionFailureException: Unable to connect to Redis
RedisCommandTimeoutException: Command timed out after 3 second(s)   // Lettuce
NoSuchElementException: Unable to validate object                    // commons-pool2 取不到连接

// 常见原因：
// 1. max-wait 设置过短或 max-active 过小
// 2. 大 Key/热 Key 导致连接长时间占用
// 3. 未设置命令 timeout，慢查询阻塞连接
// 4. 集群模式下连接数 = 节点数 × 连接池大小，容易超出 maxclients
```

---

## 七、数据持久化

```bash
# RDB 快照（推荐）
save 900 1      # 900 秒内至少 1 次修改
save 300 10     # 300 秒内至少 10 次修改
save 60 10000   # 60 秒内至少 10000 次修改

# AOF 追加（更安全）
appendonly yes
appendfsync everysec  # 每秒同步
```

---

## 八、常用命令速查

```bash
# 字符串
SET key value [EX seconds]
GET key
INCR key

# Hash
HSET key field value
HGET key field
HGETALL key

# List
LPUSH key value
RPUSH key value
LRANGE key 0 -1

# Set
SADD key member
SMEMBERS key
SINTER key1 key2

# Sorted Set
ZADD key score member
ZRANGE key 0 -1 WITHSCORES
ZREVRANK key member

# 过期
EXPIRE key seconds
TTL key
PERSIST key

# 发布订阅
PUBLISH channel message
SUBSCRIBE channel
```

---

## 九、代码审查清单

- [ ] Key 命名规范
- [ ] 设置合理过期时间
- [ ] 过期时间有随机化
- [ ] 防穿透/击穿/雪崩
- [ ] 大 Key 已拆分
- [ ] 批量操作用 Pipeline
- [ ] 敏感数据已加密
- [ ] **连接池参数合理（max-wait 非 -1、设置了命令 timeout）**
- [ ] **Redisson 锁超时时间合理**（参考 [Redisson 指南](references/redisson-guide.md)）

---

*参考：Redis Official Documentation + 阿里巴巴 Java 开发手册 + Redisson 官方文档*
