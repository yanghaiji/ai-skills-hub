# redis-standards

Redis 使用规范 Skill。

## 内容

| 文件 | 说明 |
|------|------|
| [SKILL.md](./SKILL.md) | 主规范：键设计、数据结构、缓存策略、连接池（Lettuce/Jedis）、穿透/击穿/雪崩防护、性能、持久化、命令速查 |
| [references/redisson-guide.md](./references/redisson-guide.md) | 扩展参考：Redisson 配置、分布式锁、高级锁、分布式对象、最佳实践 |

## 何时触发

- 使用 Redis 缓存、设计缓存策略时
- 编写 Redis / Redisson 相关代码时

主文档 `SKILL.md` 为唯一激活入口，涉及 Redisson 时按需加载 `references/redisson-guide.md`。
