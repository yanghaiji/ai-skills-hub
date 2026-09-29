# SQL 编写规范

适用于 MySQL/PostgreSQL/Oracle 及国产数据库的标准 SQL 编写规范。

## 目录结构

```
sql-standards/
├── SKILL.md           # 完整规范文档
└── README.md          # 本文件
```

## 核心规范模块

| 模块 | 描述 |
|------|------|
| 命名规范 | 数据库、表、字段、索引命名 |
| 表结构设计 | 主键、字段类型、约束、注释 |
| 查询规范 | SELECT、WHERE、JOIN、子查询 |
| 分页查询 | LIMIT/OFFSET、游标分页 |
| 索引设计 | 索引原则、避免失效、数量控制 |
| 性能优化 | EXPLAIN、慢查询、批量操作 |
| 事务规范 | 事务边界、锁使用 |
| 安全规范 | SQL 注入防护、权限控制 |
| **国产数据库适配** | 达梦、金仓、OceanBase、TiDB、openGauss |

## 国产数据库支持

| 数据库 | 兼容模式 | 主要用途 |
|--------|----------|----------|
| 达梦 (DM) | Oracle | 信创政企 |
| 人大金仓 (KingbaseES) | PostgreSQL | 信创政企 |
| OceanBase | MySQL/Oracle | 分布式金融 |
| TiDB | MySQL | 分布式 HTAP |
| openGauss | PostgreSQL | 华为生态 |
| GaussDB | PostgreSQL | 华为企业版 |
| PolarDB | MySQL/PG | 阿里云 |

## 使用方式

```
请按照 SQL 编写规范编写以下查询：[需求描述]

# 指定国产数据库
请按照 SQL 编写规范（达梦数据库）编写以下查询：[需求描述]
```

## 关键速查

```sql
-- 分页（MySQL）
SELECT * FROM user ORDER BY id LIMIT 10 OFFSET 0;

-- 分页（达梦/Oracle）
SELECT * FROM user ORDER BY id FETCH FIRST 10 ROWS ONLY;

-- 自增主键（MySQL）
id BIGINT PRIMARY KEY AUTO_INCREMENT

-- 自增主键（PostgreSQL/openGauss）
id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY

-- 自增主键（达梦）
id BIGINT PRIMARY KEY IDENTITY(1,1)
```

*基于：MySQL + PostgreSQL + 国产数据库适配经验*
