---
name: sql-standards
description: "SQL 编写规范：表结构设计、命名规范、查询规则、更新删除、性能考量。触发条件：编写SQL时，检测SQL语句。"
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# SQL 编写规范

参考《阿里巴巴 Java 开发手册》，适用于所有关系型数据库。

## 何时激活

* 编写 SQL 查询语句时
* 创建/修改表结构时
* **每次让AI编写SQL代码时必须触发此规范**

---

## 一、表结构设计

### 1.1 必须有主键
```sql
-- ✅ 每张表必须有主键
CREATE TABLE user (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
```

### 1.2 字段类型选择
```sql
-- 金额：必须用 DECIMAL，禁止 FLOAT/DOUBLE
price DECIMAL(10,2)

-- 布尔：TINYINT 或 BOOLEAN
is_paid TINYINT DEFAULT 0

-- 字符串：
-- VARCHAR 不确定长度时用 VARCHAR(255)
-- CHAR 用于固定长度（如MD5、身份证）
-- TEXT 存储大文本，不要放在主表

-- 时间：TIMESTAMP 或 DATETIME
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

-- IP地址：VARCHAR(15)，不要用 INT
ip_address VARCHAR(15)
```

### 1.3 字段约束
```sql
CREATE TABLE user (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL DEFAULT '',     -- 禁止 NULL 用空串代替
    email VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 0 AND age <= 150),   -- 业务约束
    status TINYINT DEFAULT 1
);
```

### 1.4 冗余字段
```sql
-- ✅ 合理冗余：减少 JOIN，空间换时间
CREATE TABLE order_item (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    product_name VARCHAR(200) NOT NULL,    -- 冗余：避免关联商品表
    product_price DECIMAL(10,2) NOT NULL   -- 冗余：快照价格
);

-- ❌ 过度冗余：数据不一致风险
-- 不要冗余经常变更的字段
```

### 1.5 必备字段
```sql
-- 每张表建议有
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     -- 创建时间
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     -- 更新时间
is_deleted TINYINT DEFAULT 0                        -- 逻辑删除
```

---

## 二、命名规范

### 2.1 库名
```sql
-- 小写+下划线，与项目名相关
CREATE DATABASE my_project;
```

### 2.2 表名
```sql
-- 小写+下划线，单数形式，业务前缀
CREATE TABLE sys_user (         -- 系统表用 sys_ 前缀
    id BIGINT PRIMARY KEY
);

CREATE TABLE biz_order (        -- 业务表用 biz_ 前缀
    id BIGINT PRIMARY KEY
);
```

### 2.3 字段名
```sql
CREATE TABLE user (
    id BIGINT PRIMARY KEY,            -- 主键统一用 id
    user_name VARCHAR(100),           -- 小写+下划线
    is_vip TINYINT,                   -- 布尔字段：is_/has_/can_ 前缀
    created_at TIMESTAMP,             -- 时间字段：_at 后缀
    order_count INT                   -- 计数字段：_count 后缀
);
```

### 2.4 索引名
```sql
CREATE INDEX idx_user_email ON user(email);        -- 普通索引
CREATE UNIQUE INDEX uk_user_email ON user(email);  -- 唯一索引
CREATE INDEX idx_order_uid_time ON order(user_id, created_at);  -- 组合索引
```

---

## 三、查询规则

### 3.1 禁止 SELECT *
```sql
-- ❌ 禁止
SELECT * FROM user WHERE id = 1;

-- ✅ 必须明确字段
SELECT id, name, email FROM user WHERE id = 1;
```

### 3.2 WHERE 条件
```sql
-- ❌ 禁止在列上使用函数
WHERE YEAR(created_at) = 2024
WHERE DATE_FORMAT(created_at, '%Y-%m') = '2024-01'

-- ✅ 范围查询
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'

-- ❌ 禁止隐式转换
WHERE phone = 13800138000      -- phone 是 VARCHAR

-- ✅ 类型匹配
WHERE phone = '13800138000'
```

### 3.3 联表查询
```sql
-- ✅ 必须使用显式 JOIN
SELECT u.id, u.name, o.order_no
FROM user u
INNER JOIN order o ON u.id = o.user_id
WHERE u.id = 1;

-- ❌ 禁止隐式联表
SELECT u.id, o.order_no
FROM user u, order o
WHERE u.id = o.user_id;

-- ✅ 小表驱动大表（JOIN 顺序）
-- user 是小表，order 是大表
SELECT u.id, u.name
FROM user u
INNER JOIN order o ON u.id = o.user_id;
```

### 3.4 子查询
```sql
-- ✅ 优先使用 EXISTS
SELECT * FROM user u
WHERE EXISTS (
    SELECT 1 FROM order o 
    WHERE o.user_id = u.id AND o.status = 'paid'
);

-- ✅ IN 适合小数据量
SELECT * FROM user 
WHERE id IN (SELECT user_id FROM order WHERE status = 'paid');
```

### 3.5 分页查询
```sql
-- ✅ 小偏移量：LIMIT + OFFSET
SELECT id, name FROM user ORDER BY id LIMIT 10 OFFSET 0;

-- ✅ 大偏移量：游标分页
SELECT id, name FROM user WHERE id > 1000000 ORDER BY id LIMIT 10;
```

---

## 四、更新删除操作

### 4.1 UPDATE 规范
```sql
-- ✅ 必须带 WHERE 条件
UPDATE user SET status = 1 WHERE id = 1;

-- ❌ 禁止不带 WHERE（全表更新）
UPDATE user SET status = 1;

-- ✅ 批量更新指定 ID
UPDATE user SET status = 1 WHERE id IN (1, 2, 3);
```

### 4.2 DELETE 规范
```sql
-- ✅ 必须带 WHERE 条件
DELETE FROM user WHERE id = 1;

-- ❌ 禁止不带 WHERE（全表删除）
DELETE FROM user;

-- ✅ 大批量删除（分批）
DELETE FROM user WHERE id BETWEEN 1 AND 1000;
DELETE FROM user WHERE id BETWEEN 1001 AND 2000;
```

### 4.3 逻辑删除
```sql
-- ✅ 推荐逻辑删除
UPDATE user SET is_deleted = 1 WHERE id = 1;

-- ✅ 查询时排除已删除
SELECT * FROM user WHERE is_deleted = 0;
```

### 4.4 批量操作
```sql
-- ✅ 批量插入
INSERT INTO user (name, email) VALUES
('John', 'john@test.com'),
('Jane', 'jane@test.com');

-- ✅ 批量更新（同一字段）
UPDATE user SET status = 1 WHERE id IN (1, 2, 3);

-- ❌ 禁止逐条操作（循环插入）
-- 应在应用层批量处理
```

---

## 五、性能考量

### 5.1 索引原则
```sql
-- ✅ WHERE、JOIN、ORDER BY 字段必须有索引
CREATE INDEX idx_order_user_id ON order(user_id);

-- ✅ 组合索引遵循最左前缀
CREATE INDEX idx_order_uid_status ON order(user_id, status);
-- 可用：WHERE user_id = ?
-- 可用：WHERE user_id = ? AND status = ?
-- 不可用：WHERE status = ?
```

### 5.2 避免索引失效
```sql
-- ❌ 索引失效场景
WHERE YEAR(created_at) = 2024        -- 函数
WHERE status != 'deleted'            -- 不等于
WHERE name LIKE '%test'             -- 左通配
WHERE email = 'a' OR phone = 'b'    -- OR 连接非索引列

-- ✅ 改写方式
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
WHERE status IN ('active', 'pending')
WHERE name LIKE 'test%'
```

### 5.3 EXPLAIN 必须掌握
```sql
EXPLAIN SELECT * FROM user WHERE email = 'test@test.com';

-- 关键字段：
-- type: ALL(全表) → ref(索引) → const(主键)  [必须到 ref 以上]
-- key: 使用的索引
-- rows: 扫描行数（越少越好）
-- Extra: Using filesort/Using temporary [出现需优化]
```

### 5.4 大表操作
```sql
-- ✅ 大表 DDL 使用 Online DDL
ALTER TABLE user ADD INDEX idx_email (email), ALGORITHM=INPLACE, LOCK=NONE;

-- ✅ 大表数据迁移分批
UPDATE user SET status = 'done' WHERE id BETWEEN 1 AND 1000;
UPDATE user SET status = 'done' WHERE id BETWEEN 1001 AND 2000;

-- ✅ 超大数据量考虑分区
-- 按时间分区
```

### 5.5 性能禁忌
```sql
-- ❌ 大偏移分页
SELECT * FROM user ORDER BY id LIMIT 10 OFFSET 1000000;

-- ❌ 大表全表扫描
SELECT * FROM big_table WHERE name = 'test';  -- name 无索引

-- ❌ 大事务
-- 一次更新超过 1 万条记录

-- ❌ 在 SQL 中做复杂计算
-- 应在应用层处理
```

---

## 代码审查清单

- [ ] 表必须有主键
- [ ] 金额用 DECIMAL
- [ ] 禁止 SELECT *
- [ ] WHERE 无函数、无隐式转换
- [ ] JOIN 用显式语法
- [ ] UPDATE/DELETE 必须带 WHERE
- [ ] 大批量操作已分批
- [ ] 关键查询已 EXPLAIN 验证

---

*参考：《阿里巴巴 Java 开发手册》MySQL 篇*
