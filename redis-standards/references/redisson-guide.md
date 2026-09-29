# Redisson 使用指南

> 本文是 [redis-standards](../SKILL.md) 的扩展参考，聚焦 Redisson 客户端的分布式锁与分布式对象用法。基础的键设计、缓存策略、穿透/击穿/雪崩等请先看主文档。

---

## 一、依赖与配置

### 1.1 Maven 依赖
```xml
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <!-- 版本由父 POM / BOM 统一管理，无需在此写死 -->
</dependency>
```

### 1.2 单机模式配置
```java
@Configuration
public class RedissonConfig {

    @Bean
    public RedissonClient redissonClient() {
        Config config = new Config();
        config.useSingleServer()
              .setAddress("redis://localhost:6379")
              .setDatabase(0)
              .setPassword("your_password")
              // ===== 连接池 =====
              .setConnectionPoolSize(64)        // 连接池最大连接数，默认 64
              .setConnectionMinimumIdleSize(24) // 最小空闲连接，默认 24
              .setIdleConnectionTimeout(10000)  // 空闲连接回收（毫秒）
              // ===== 超时与重试 =====
              .setConnectTimeout(10000)         // 连接超时（毫秒）
              .setTimeout(3000)                 // 命令响应超时（毫秒）
              .setRetryAttempts(3)              // 命令重试次数
              .setRetryInterval(1500);          // 重试间隔（毫秒）
        return Redisson.create(config);
    }
}
```

### 1.3 集群模式配置
```java
config.useClusterServers()
      // 主节点连接池
      .setMasterConnectionPoolSize(64)
      .setMasterConnectionMinimumIdleSize(24)
      // 从节点连接池
      .setSlaveConnectionPoolSize(64)
      .setSlaveConnectionMinimumIdleSize(24)
      .setConnectTimeout(10000)
      .setTimeout(3000)
      .setRetryAttempts(3)
      .setRetryInterval(1500)
      .setScanInterval(2000)  // 集群节点状态扫描间隔（毫秒）
      .addNodeAddress("redis://node1:6379",
                      "redis://node2:6379",
                      "redis://node3:6379");
```

### 1.4 YAML 等价写法
```yaml
# redisson.yml
singleServerConfig:
  address: "redis://localhost:6379"
  database: 0
  password: "your_password"
  connectionPoolSize: 64
  connectionMinimumIdleSize: 24
  idleConnectionTimeout: 10000
  connectTimeout: 10000
  timeout: 3000
  retryAttempts: 3
  retryInterval: 1500
```

### 1.5 连接池参数说明
| 参数 | 默认值 | 说明 |
|------|--------|------|
| connectionPoolSize | 64 | 连接池上限；过小高并发阻塞，过大增加 Redis 负担 |
| connectionMinimumIdleSize | 24 | 预热空闲连接，避免突发流量频繁建连 |
| timeout | 3000 | 命令响应超时，❌ 不设则慢查询长期占用连接 |
| retryAttempts / retryInterval | 3 / 1500 | 失败重试次数与间隔，配合幂等操作使用 |
| idleConnectionTimeout | 10000 | 空闲连接回收时间 |
| subscriptionConnectionPoolSize | 50 | 仅在使用发布订阅时需要关注 |

> ⚠️ **集群注意**：实际总连接数 ≈ 节点数 × connectionPoolSize，需确保不超过 Redis 服务端 `maxclients`（默认 10000）。

---

## 二、分布式锁

### 2.1 标准加锁模板（推荐）
```java
RLock lock = redissonClient.getLock("business_lock");
boolean isLocked = false;
try {
    // 最多等待 1 秒，加锁后 10 秒自动释放
    isLocked = lock.tryLock(1, 10, TimeUnit.SECONDS);
    if (!isLocked) {
        throw new RuntimeException("获取分布式锁失败");
    }
    doBusiness();
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();   // 恢复中断状态
    throw new RuntimeException(e);
} finally {
    // ✅ 只有当前线程持有锁时才释放，避免误删他人锁
    if (isLocked && lock.isHeldByCurrentThread()) {
        lock.unlock();
    }
}
```

### 2.2 可重入锁
```java
RLock lock = redissonClient.getLock("business_lock");

lock.lock();  // 第一次加锁
lock.lock();  // 同一线程再次加锁，不会阻塞
try {
    doBusiness();
} finally {
    lock.unlock();  // 第一次解锁
    lock.unlock();  // 第二次解锁，真正释放
}
```

### 2.3 看门狗机制（长时间任务）
```java
RLock lock = redissonClient.getLock("long_task_lock");

// 不指定 leaseTime，启动看门狗自动续期（默认锁 30 秒，每 10 秒续一次）
lock.lock();
try {
    longRunningTask();  // 执行时间不确定/较长的任务
} finally {
    lock.unlock();
}
// ⚠️ 一旦显式传入 leaseTime，看门狗不生效，锁到期强制释放
```

---

## 三、高级锁

### 3.1 多锁组合（MultiLock）
```java
RLock lock1 = redissonClient.getLock("order:lock");
RLock lock2 = redissonClient.getLock("inventory:lock");
RLock lock3 = redissonClient.getLock("payment:lock");

// 全部加锁成功才返回 true，任意一个失败则全部释放
RedissonMultiLock multiLock = new RedissonMultiLock(lock1, lock2, lock3);
boolean isLocked = false;
try {
    isLocked = multiLock.tryLock(3, 30, TimeUnit.SECONDS);
    if (isLocked) {
        processOrder();
    }
} finally {
    if (isLocked) {
        multiLock.unlock();
    }
}
```

### 3.2 红锁（RedLock）
```java
// ⚠️ RedLock 存在争议，仅在跨多个独立 Redis 实例的强一致场景谨慎评估使用
RLock redLock = redissonClient.getRedLock(
    redissonClient.getLock("lock1"),
    redissonClient.getLock("lock2"),
    redissonClient.getLock("lock3")
);
boolean isLocked = redLock.tryLock(1, 10, TimeUnit.SECONDS);
```

### 3.3 读写锁（ReadWriteLock）
```java
RReadWriteLock rwLock = redissonClient.getReadWriteLock("resource_lock");

// 读读共享
RLock readLock = rwLock.readLock();
// 读写/写写互斥
RLock writeLock = rwLock.writeLock();
```

### 3.4 信号量（Semaphore）
```java
RSemaphore semaphore = redissonClient.getSemaphore("api_limit");
semaphore.trySetPermits(100);                 // 初始化许可数
if (semaphore.tryAcquire(3, 10, TimeUnit.SECONDS)) {
    try {
        doBusiness();                          // 获取 3 个许可
    } finally {
        semaphore.release(3);                  // 释放许可
    }
}
```

---

## 四、分布式对象

### 4.1 原子计数器
```java
RAtomicLong counter = redissonClient.getAtomicLong("visit_counter");
counter.incrementAndGet();  // 原子递增
counter.addAndGet(10);      // 增加指定值
long value = counter.get(); // 获取当前值
```

### 4.2 限流信号量示例
```java
public boolean allowAccess(String userId) {
    RSemaphore semaphore = redissonClient.getSemaphore("rate_limit:" + userId);
    semaphore.trySetPermits(10);
    return semaphore.tryAcquire(1, 1, TimeUnit.SECONDS);
}
```

### 4.3 阻塞队列
```java
RBlockingQueue<String> queue = redissonClient.getBlockingQueue("task_queue");
queue.put("task1");           // 阻塞式放入
String task = queue.take();   // 阻塞式取出
```

### 4.4 Set / Sorted Set
```java
// 集合
RSet<String> onlineUsers = redissonClient.getSet("online_users");
onlineUsers.add("user:1001");

// 排行榜（带分数的有序集合）
RScoredSortedSet<String> leaderboard = redissonClient.getScoredSortedSet("leaderboard");
leaderboard.add(100.0, "user:1001");
leaderboard.add(95.0, "user:1002");
Collection<String> top10 = leaderboard.valueRangeRev(0, 9);  // 前 10 名
```

---

## 五、最佳实践

### 5.1 锁粒度：越细越好
```java
// ✅ 细粒度：锁定具体资源
RLock lock = redissonClient.getLock("order:12345:lock");

// ❌ 粗粒度：锁定整个模块，无谓阻塞
RLock lock = redissonClient.getLock("order:lock");
```

### 5.2 leaseTime 按业务耗时设置
```java
// ✅ 略大于业务预计耗时
lock.tryLock(1, 5, TimeUnit.SECONDS);

// ❌ 拍脑袋固定值，太短业务没跑完锁就掉了
lock.tryLock(1, 10, TimeUnit.SECONDS);
```

### 5.3 多资源加锁保证顺序，防止死锁
```java
// 对多个 key 加锁时，按固定顺序（如字典序）获取，避免交叉等待
List<RLock> locks = Stream.of("account:B:lock", "account:A:lock")
    .sorted()
    .map(redissonClient::getLock)
    .collect(Collectors.toList());
```

---

## 代码审查清单

- [ ] 使用了 `tryLock` 而非无参 `lock()`
- [ ] leaseTime（超时时间）按业务耗时合理设置
- [ ] `finally` 中用 `isHeldByCurrentThread()` 判断后再 `unlock`
- [ ] 捕获 `InterruptedException` 并恢复中断状态
- [ ] 长时间任务依赖看门狗续期（不显式设 leaseTime）
- [ ] 多锁组合注意死锁风险，加锁顺序一致
- [ ] 连接池参数合理，总连接数不超过服务端 `maxclients`

---

*参考：Redisson 官方文档*
