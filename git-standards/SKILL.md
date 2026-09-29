---
name: git-standards
description: "Git 工作规范：提交信息、分支策略、Code Review、协作流程。触发条件：Git操作、提交代码、创建分支、代码审查时。"
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# Git 工作规范

适用于团队协作的 Git 工作流程和最佳实践。

## 何时激活

* 提交代码时
* 创建/合并分支时
* 进行 Code Review 时
* **每次让AI操作Git时必须触发此规范**

---

## 一、提交信息规范

### 1.1 格式（Conventional Commits）
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 1.2 Type 类型
| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 Bug |
| docs | 文档变更 |
| style | 代码格式（不影响功能） |
| refactor | 重构（非新功能、非修复） |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建、工具、依赖变更 |
| ci | CI 配置变更 |

### 1.3 示例
```bash
# ✅ 好的提交
feat(user): 添加用户注册功能

- 实现手机号注册
- 添加短信验证码验证
- 集成阿里云短信服务

Closes #123

# ❌ 差的提交
update code
fix bug
```

### 1.4 规则
- subject 不超过 50 字符
- subject 用祈使语气（"添加" 而非 "添加了"）
- 首字母小写，不加句号
- body 说明 WHY 而非 WHAT

---

## 二、分支策略

### 2.1 分支模型（Git Flow 简化版）
```
main (master)     ← 生产环境，只接受 PR
  ↑
release/*         ← 预发布分支（可选）
  ↑
develop           ← 开发主干
  ↑
feature/*         ← 功能分支
hotfix/*          ← 紧急修复
```

### 2.2 分支命名
```bash
# 功能分支
feature/user-registration
feature/payment-integration

# 修复分支
bugfix/login-error
hotfix/security-vulnerability

# 发布分支
release/v1.2.0
```

### 2.3 工作流程
```bash
# 1. 从 develop 创建功能分支
git checkout develop
git checkout -b feature/user-login

# 2. 开发并提交
git add .
git commit -m "feat(auth): 添加登录接口"

# 3. 推送并创建 PR
git push origin feature/user-login
# 在 GitHub/GitLab 创建 PR → develop

# 4. Code Review 通过后合并
# 5. 删除功能分支
git branch -d feature/user-login
```

---

## 三、Code Review 规范

### 3.1 Review 检查项
- [ ] 代码逻辑是否正确
- [ ] 是否有潜在 Bug
- [ ] 是否有安全隐患
- [ ] 代码是否可读
- [ ] 是否有重复代码
- [ ] 测试是否充分
- [ ] 命名是否清晰

### 3.2 Review 礼仪
```markdown
# ✅ 建议性 comment
建议考虑使用 Optional 避免 NPE

# ❌ 指令性 comment
必须改成 Optional

# ✅ 解释原因
这里可能有并发问题，建议使用 ConcurrentHashMap
```

### 3.3 PR 规范
```markdown
## 描述
简要说明这个 PR 做了什么

## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 重构
- [ ] 文档更新

## 测试
- [ ] 已添加单元测试
- [ ] 已手动测试

## 关联 Issue
Closes #123
```

---

## 四、Git 操作规范

### 4.1 .gitignore 必须包含
```gitignore
# 依赖
node_modules/
vendor/
target/

# 编译产物
dist/
build/
*.class
*.jar

# IDE
.idea/
.vscode/
*.swp

# 环境
.env
.env.local
*.local

# 日志
*.log
logs/
```

### 4.2 禁止操作
```bash
# ❌ 禁止强制推送主分支
git push --force origin main

# ❌ 禁止直接提交到 main/develop
git checkout main
git commit -m "..."  # 应该通过 PR

# ❌ 禁止提交敏感信息
password = "123456"
API_KEY = "xxx"
```

### 4.3 敏感信息处理
```bash
# 如果意外提交了敏感信息
# 1. 立即撤销
git revert HEAD

# 2. 修改密码/密钥
# 3. 使用 git filter-branch 清理历史（谨慎）
```

---

## 五、Commit 规范速查

| 场景 | 格式 |
|------|------|
| 新功能 | `feat(scope): 描述` |
| 修复 Bug | `fix(scope): 描述` |
| 文档 | `docs: 描述` |
| 重构 | `refactor(scope): 描述` |
| 性能 | `perf(scope): 描述` |
| 测试 | `test: 描述` |
| 构建 | `chore: 描述` |

---

## 代码审查清单

- [ ] 提交信息符合规范
- [ ] 分支命名正确
- [ ] 代码已自我审查
- [ ] 敏感信息已脱敏
- [ ] 测试已添加/更新
- [ ] 文档已更新（如需要）

---

*参考：Conventional Commits + Git Flow + GitHub Flow*
