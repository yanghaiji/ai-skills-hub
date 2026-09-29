---
name: docker-standards
description: "Docker 最佳实践：镜像构建、多阶段构建、安全、优化。触发条件：编写Dockerfile、构建镜像时。"
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# Docker 最佳实践

适用于现代容器化应用的 Docker 镜像构建标准。

## 何时激活

* 编写 Dockerfile 时
* 构建 Docker 镜像时
* **每次让AI编写Docker配置时必须触发此规范**

---

## 一、Dockerfile 规范

### 1.1 基础镜像选择
```dockerfile
# ✅ 使用官方精简镜像
FROM eclipse-temurin:17-jre-alpine
FROM node:20-alpine
FROM python:3.12-slim

# ❌ 避免使用
FROM ubuntu:latest  # 体积大
FROM node:20        # 完整版，体积大
```

### 1.2 多阶段构建
```dockerfile
# 阶段1：构建
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

# 阶段2：运行
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 1.3 层缓存优化
```dockerfile
# ✅ 先复制依赖文件，再复制源码
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src

# ❌ 源码变更导致依赖重新下载
COPY . .
RUN mvn package
```

---

## 二、镜像优化

### 2.1 减少层数
```dockerfile
# ✅ 合并 RUN 命令
RUN apk add --no-cache curl \
    && rm -rf /var/cache/apk/*

# ❌ 多个 RUN 命令
RUN apk add curl
RUN rm -rf /var/cache/apk/*
```

### 2.2 清理缓存
```dockerfile
# ✅ 清理构建缓存
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# ✅ 清理不必要的文件
RUN rm -rf /tmp/* /var/tmp/*
```

### 2.3 .dockerignore
```
# 必须排除
.git
.gitignore
node_modules
target
build
*.md
.env
.idea
.vscode
```

---

## 三、安全规范

### 3.1 非 root 用户
```dockerfile
# ✅ 创建专用用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# ❌ 使用 root 运行
# 默认 root，不安全
```

### 3.2 只读文件系统
```yaml
# docker-compose.yml
services:
  app:
    image: myapp
    read_only: true
    tmpfs:
      - /tmp
```

### 3.3 安全扫描
```bash
# 扫描镜像漏洞
docker scout cves myimage:latest
trivy image myimage:latest
```

---

## 四、配置管理

### 4.1 环境变量
```dockerfile
# ✅ 使用 ENV 设置默认值
ENV JAVA_OPTS="-Xms512m -Xmx512m"

# ✅ 运行时可覆盖
CMD ["java", "-jar", "app.jar"]
```

### 4.2 健康检查
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

### 4.3 暴露端口
```dockerfile
# ✅ 仅声明必要端口
EXPOSE 8080

# ❌ 暴露过多端口
EXPOSE 8080 3000 5000 9090
```

---

## 五、最佳实践

### 5.1 固定版本
```dockerfile
# ✅ 固定版本
FROM node:20.10-alpine
FROM eclipse-temurin:17.0.9-jre-alpine

# ❌ 使用 latest
FROM node:latest
```

### 5.2 COPY vs ADD
```dockerfile
# ✅ 使用 COPY（更明确）
COPY requirements.txt .
COPY target/*.jar app.jar

# ⚠️ ADD 仅在需要自动解压时使用
ADD archive.tar.gz /app/
```

### 5.3 WORKDIR
```dockerfile
# ✅ 使用 WORKDIR 替代 cd
WORKDIR /app
COPY . .

# ❌ 避免
RUN mkdir -p /app
WORKDIR /app
```

---

## 六、Docker Compose 规范

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: myapp:latest
    container_name: myapp
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

---

## 七、常用命令

```bash
# 构建镜像
docker build -t myapp:latest .

# 运行容器
docker run -d -p 8080:8080 --name myapp myapp:latest

# 查看日志
docker logs -f myapp

# 进入容器
docker exec -it myapp sh

# 清理
docker system prune -a
```

---

## 代码审查清单

- [ ] 使用官方精简基础镜像
- [ ] 多阶段构建
- [ ] 非 root 用户运行
- [ ] .dockerignore 配置
- [ ] 固定版本号
- [ ] 健康检查配置
- [ ] 无敏感信息硬编码

---

*参考：Docker Best Practices + Alpine Linux + 12-Factor App*
