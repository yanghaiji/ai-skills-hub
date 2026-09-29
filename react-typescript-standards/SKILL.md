---
name: react-typescript-standards
description: "React + TypeScript 前端开发规范：组件设计、类型安全、状态管理、性能优化、代码风格。触发条件：编写React代码、创建组件、实现页面、代码审查、重构前端代码时。支持项目级规范覆盖。"
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# React + TypeScript 前端开发规范

适用于 React 18+/19 和 TypeScript 5+ 的现代前端应用开发标准。

## 何时激活

* 在 React 项目中编写或审查代码时
* 创建新组件或重构现有组件时
* 实现状态管理、数据获取、表单处理时
* **每次让 AI 编写前端代码时必须触发此规范**

## 核心原则

* 类型安全优先：充分利用 TypeScript 静态类型检查
* 组件单一职责：每个组件只做一件事
* 不可变数据：状态更新产生新引用
* 组合优于继承：优先使用组合模式
* 清晰的代码结构：易于维护和扩展

---

## 项目级规范覆盖

项目可在以下位置放置自定义规范文件，**优先级高于本 Skill 默认规范**：
- `.qoder/specs/` — 项目级规范目录（随代码库提交）
- 支持 `.md` 格式的前端规范文件

**优先级**：项目级规范 > 本 Skill 默认规范

---

## 一、TypeScript 规范

### 1.1 类型定义优先，禁止 any
```typescript
// PASS: 明确类型 + unknown + 类型守卫
interface User { id: number; name: string; role: UserRole; }
function processData(input: unknown) {
  if (typeof input === 'string') return input.toUpperCase();
  return input;
}

// FAIL
const user: any = { id: 1 };
function processData(input: any) { return input.toUpperCase(); }
```

### 1.2 Interface 用于对象形状，Type 用于联合/交叉
```typescript
interface ApiResponse<T> { code: number; message: string; data: T; }
type UserRole = 'admin' | 'user' | 'guest';
type UserWithPosts = User & { posts: Post[] };
```

### 1.3 const 断言 + 枚举规范
```typescript
const ROUTES = { HOME: '/', ABOUT: '/about' } as const;

// 枚举：优先联合类型，或 const enum
type Status = 'ACTIVE' | 'INACTIVE' | 'PENDING';
```

### 1.4 泛型组件/函数
```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
}
function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return <ul>{items.map(item => <li key={keyExtractor(item)}>{renderItem(item)}</li>)}</ul>;
}
```

---

## 二、组件设计规范

### 2.1 命名：PascalCase，描述性
```typescript
// PASS
function UserProfile() {}
// FAIL
function userProfile() {} function UA() {}
```

### 2.2 Props 设计原则
```typescript
// PASS: interface 定义 + 解构 + 默认值
interface UserCardProps { user: User; showEmail?: boolean; onSelect?: (userId: number) => void; }
function UserCard({ user, showEmail = true, onSelect }: UserCardProps) {
  return <div onClick={() => onSelect?.(user.id)}><h3>{user.name}</h3>{showEmail && <p>{user.email}</p>}</div>;
}

// FAIL: any props
function UserCard(props: any) { return <div>{props.user.name}</div>; }
```

### 2.3 Children 类型用 React.ReactNode
```typescript
interface CardProps { title: string; children: React.ReactNode; footer?: React.ReactNode; }
```

### 2.4 组件文件结构
- **简单组件**：单文件 `.tsx`
- **复杂组件**：拆分为 `Component.tsx` + `Component.types.ts` + `Component.styles.ts` + `index.ts`

---

## 三、Hooks 规范

### 3.1 命名：use + 功能描述
```typescript
// PASS
function useUserData(userId: number) { ... }
// FAIL
function getUserData() { ... }
```

### 3.2 useState：明确类型 + 函数式更新
```typescript
const [user, setUser] = useState<User | null>(null);
setItems(prev => [...prev, newItem]);  // PASS
setItems([...items, newItem]);          // FAIL: 依赖外部变量
```

### 3.3 useEffect：正确依赖 + 清理函数
```typescript
useEffect(() => { fetchData(userId); }, [userId]);  // PASS
useEffect(() => { fetchData(userId); }, []);         // FAIL: 缺少依赖
useEffect(() => {
  const timer = setInterval(() => {}, 1000);
  return () => clearInterval(timer);  // PASS: 清理
}, []);
```

### 3.4 useCallback/useMemo：只在必要时使用
```typescript
// PASS: 传给 memo 子组件或计算开销大时使用
const handleSubmit = useCallback((data: FormData) => { submitForm(data); }, [submitForm]);
const sortedItems = useMemo(() => [...items].sort((a, b) => a.name.localeCompare(b.name)), [items]);
```

---

## 四、状态管理

### 4.1 状态分层
| 层级 | 场景 | 方案 |
|------|------|------|
| 组件本地状态 | UI 状态（开关、选中） | `useState` |
| 共享状态 | 跨组件共享 | `Context` / 状态管理库 |
| 服务器状态 | API 数据 | `React Query` / `SWR` |

### 4.2 不可变更新
```typescript
setUser({ ...user, name: 'New Name' });
setItems(prev => prev.map(item => item.id === targetId ? { ...item, completed: true } : item));
// FAIL: 直接修改
user.name = 'New Name';
```

### 4.3 复杂状态用 useReducer
当状态逻辑涉及多个子值或下一个状态依赖之前状态时，使用 `useReducer` 替代多个 `useState`。

---

## 五、组件模式

### 5.1 容器/展示分离
- **Container**：负责数据获取和业务逻辑
- **Presentational**：纯 UI 展示，通过 props 接收数据

### 5.2 Compound Components
适合 Tabs、Accordion 等组件族，通过 `Context` 共享隐式状态。

### 5.3 Render Props
适合需要反转控制权的场景，但优先使用自定义 Hook 替代。

---

## 六、性能优化

| 优化项 | 方案 |
|--------|------|
| 代码分割 | `React.lazy()` + `<Suspense>` |
| 列表渲染 | 大数据用虚拟滚动（`react-window`） |
| 避免重渲染 | `React.memo` + `useMemo` + `useCallback` |
| 图片 | `loading="lazy"` 或 Next.js `<Image>` |
| key | 使用稳定唯一 ID，**禁止用 index 作为 key**（列表会变动时） |

---

## 七、样式规范

按项目技术栈选择一种方案，**项目内保持一致**：

| 方案 | 适用场景 |
|------|----------|
| CSS Module | 中小型项目，无额外依赖 |
| Tailwind CSS | 快速开发，原子化 CSS |
| Styled Components | 动态样式需求强 |
| CSS-in-JS (vanilla-extract) | 类型安全的零运行时方案 |

---

## 八、错误处理

### 8.1 Error Boundary
每个路由/模块级组件应包裹 Error Boundary，防止白屏。

### 8.2 异步错误
- React Query：配置 `retry` + `onError`
- 全局：监听 `window.onerror` + `unhandledrejection`

---

## 九、测试规范

| 测试类型 | 工具 | 覆盖目标 |
|----------|------|----------|
| 组件测试 | Testing Library | 渲染 + 交互 |
| Hook 测试 | `renderHook` + `act` | 逻辑正确性 |
| 集成测试 | Testing Library + MSW | 完整用户流程 |
| E2E 测试 | Playwright / Cypress | 关键业务路径 |

---

## 十、前端工程化

### 10.1 ESLint + Prettier
```json
// .eslintrc.json 核心规则
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended", "plugin:react-hooks/recommended"],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

### 10.2 项目结构（参考）
```
src/
  components/     # 通用组件（Button/, Modal/...）
  pages/          # 页面组件
  hooks/          # 自定义 Hooks
  services/       # API 服务层
  types/          # TypeScript 类型定义
  utils/          # 工具函数
  constants/      # 常量
  styles/         # 全局样式
```

### 10.3 构建工具
| 场景 | 推荐 |
|------|------|
| 新项目 | Vite |
| 全栈/SSR | Next.js |
| 组件库 | tsup / rollup |

---

## 十一、React 19 新特性

| 特性 | 说明 |
|------|------|
| `use()` Hook | 在渲染中读取 Promise/Context，替代部分 `useEffect` + `useState` 模式 |
| Server Components | 服务端渲染组件，减少客户端 JS 体积 |
| Actions | 表单提交的新模式，配合 `useActionState` |
| `useFormStatus` / `useOptimistic` | 表单状态和乐观更新 |
| `ref` 作为 prop | 函数组件可直接接收 `ref` prop，不再需要 `forwardRef` |

---

## 十二、代码坏味道

| 问题 | 解决方案 |
|------|----------|
| 组件文件过长 | 拆分为更小组件 |
| Props 过多（>5个） | 使用组合模式或 children |
| 嵌套过深 | 早返回、提取子组件 |
| 重复逻辑 | 提取自定义 Hook |
| 大量 useEffect | 重新思考状态设计 |
| 复杂条件渲染 | 提取子组件或策略模式 |
| useEffect 同步派生状态 | 直接在渲染中计算 |

---

## 十三、代码审查清单

- [ ] 类型定义完整，无 `any` 使用
- [ ] 组件职责单一，文件 ≤ 200 行
- [ ] Props 使用 `interface` 定义
- [ ] Hook 依赖数组正确
- [ ] 无不必要的重渲染
- [ ] 错误边界完善
- [ ] 测试覆盖关键场景
- [ ] ESLint 无 warning

---

> ## `references/` 按需加载指令
>
> 以下文件**不会自动加载**，Agent 必须根据当前任务场景**主动读取**对应文件，并根据实际场景按需加载，避免无谓的资源消耗：
>
> | 触发场景 | 必须读取的文件 |
> |----------|----------------|
> | 需要查看某章节的完整代码示例、组件模式、Error Boundary 实现、React 19 新特性示例 | `references/examples.md` |
> | 创建新的组件、Hook、测试文件、工程化配置（ESLint/Prettier/tsconfig） | `references/templates.md` |
>
> **代码审查/检测场景**：仅使用本文件（SKILL.md）中的规则要点即可，**无需加载** references 文件，除非发现需要深入判断的边界场景。

---

**记住**：代码是写给人看的，顺便让计算机执行。优先考虑可读性和可维护性。

*基于：React 官方文档 + TypeScript 最佳实践 + Airbnb 规范*
