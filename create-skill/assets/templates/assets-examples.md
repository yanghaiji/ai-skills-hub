# Assets 模板示例

## HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{title}}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>{{title}}</h1>
    <div class="content">{{content}}</div>
  </div>
</body>
</html>
```

## 配置模板 (YAML)

```yaml
# {{project-name}} 配置文件
version: "1.0.0"

# 基础配置
app:
  name: "{{app-name}}"
  port: {{port}}
  environment: {{environment}}

# 数据库配置
database:
  host: "{{db-host}}"
  port: {{db-port}}
  name: "{{db-name}}"

# 日志配置
logging:
  level: {{log-level}}
  file: "{{log-file}}"
```

## 配置模板 (JSON)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "{{config-title}}",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "项目名称"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    }
  },
  "required": ["name", "version"]
}
```

## React 组件模板 (TSX)

```tsx
import React from 'react';

interface {{ComponentName}}Props {
  title: string;
  children?: React.ReactNode;
}

export const {{ComponentName}}: React.FC<{{ComponentName}}Props> = ({ 
  title, 
  children 
}) => {
  return (
    <div className="{{component-name}}">
      <h2>{title}</h2>
      {children}
    </div>
  );
};

export default {{ComponentName}};
```

## 环境变量模板

```bash
# {{project-name}} 环境变量
# 复制此文件为 .env 并填写实际值

# 应用配置
APP_NAME={{app-name}}
APP_PORT={{port}}
APP_ENV={{environment}}

# API 配置
API_BASE_URL={{api-url}}
API_KEY={{api-key}}

# 数据库配置
DATABASE_URL={{database-url}}

# 第三方服务
{{service-name}}_KEY={{service-key}}
```

## Docker Compose 模板

```yaml
version: '3.8'

services:
  {{service-name}}:
    build: .
    ports:
      - "{{port}}:{{port}}"
    environment:
      - NODE_ENV={{environment}}
      - DATABASE_URL={{database-url}}
    volumes:
      - .:/app
      - /app/node_modules
    command: {{start-command}}

  {{db-service-name}}:
    image: postgres:14
    environment:
      POSTGRES_DB: {{db-name}}
      POSTGRES_USER: {{db-user}}
      POSTGRES_PASSWORD: {{db-password}}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## GitHub Actions 模板

```yaml
name: {{workflow-name}}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Run tests
      run: npm test
      
    - name: Build
      run: npm run build
```

## 占位符说明

在模板中使用 `{{placeholder}}` 格式的占位符。生成时：

1. **必填占位符**：无默认值，必须询问用户
2. **可选占位符**：有默认值（如 `{{port}}` 默认 3000），用户可选择使用默认值
3. **命名规范**：使用 kebab-case（如 `{{app-name}}`、`{{db-host}}`）
4. **说明文档**：在 SKILL.md 的 `## Usage` 中列出所有占位符及其用途
