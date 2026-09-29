# React + TypeScript 详细代码示例

本文档包含 SKILL.md 中各章节的完整代码示例，供需要时查阅。

---

## 一、TypeScript 完整示例

### 泛型组件完整示例
```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map(item => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// 使用
<List<User>
  items={users}
  renderItem={(user) => <span>{user.name}</span>}
  keyExtractor={(user) => String(user.id)}
/>
```

### const 断言
```typescript
const ROUTES = {
  HOME: '/',
  ABOUT: '/about',
  USER: '/user',
} as const;

// ROUTES.HOME 类型为 '/' 而非 string
```

---

## 二、组件设计完整示例

### Props 设计 + Children + 函数 Props
```typescript
interface UserCardProps {
  user: User;
  showEmail?: boolean;
  onSelect?: (userId: number) => void;
  children?: React.ReactNode;
  footer?: React.ReactNode;
}

function UserCard({ user, showEmail = true, onSelect, children, footer }: UserCardProps) {
  return (
    <div className="card" onClick={() => onSelect?.(user.id)}>
      <h3>{user.name}</h3>
      {showEmail && <p>{user.email}</p>}
      {children}
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
}
```

### 泛型 Select 组件
```typescript
interface SelectProps<T> {
  options: T[];
  value: T | null;
  onChange: (value: T) => void;
  getLabel: (item: T) => string;
  getKey: (item: T) => string;
}

function Select<T extends { id: string }>({
  options, value, onChange, getLabel, getKey,
}: SelectProps<T>) {
  return (
    <select
      value={value?.id ?? ''}
      onChange={(e) => {
        const selected = options.find(o => getKey(o) === e.target.value);
        if (selected) onChange(selected);
      }}
    >
      {options.map(item => (
        <option key={getKey(item)} value={getKey(item)}>
          {getLabel(item)}
        </option>
      ))}
    </select>
  );
}
```

---

## 三、Hooks 完整示例

### 自定义 Hook：useLocalStorage
```typescript
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setStoredValue = useCallback((newValue: T | ((prev: T) => T)) => {
    setValue(prev => {
      const valueToStore = newValue instanceof Function ? newValue(prev) : newValue;
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
      return valueToStore;
    });
  }, [key]);

  return [value, setStoredValue] as const;
}
```

### 自定义 Hook：useDebounce
```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

---

## 四、状态管理完整示例

### useReducer 完整示例
```typescript
interface State {
  items: Item[];
  loading: boolean;
  error: string | null;
}

type Action =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: Item[] }
  | { type: 'FETCH_ERROR'; payload: string }
  | { type: 'ADD_ITEM'; payload: Item }
  | { type: 'REMOVE_ITEM'; payload: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, items: action.payload };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'ADD_ITEM':
      return { ...state, items: [...state.items, action.payload] };
    case 'REMOVE_ITEM':
      return { ...state, items: state.items.filter(i => i.id !== action.payload) };
    default:
      return state;
  }
}

// 使用
function ItemManager() {
  const [state, dispatch] = useReducer(reducer, { items: [], loading: false, error: null });
  // ...
}
```

### Context 共享状态
```typescript
interface AuthContextType {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (credentials: LoginCredentials) => {
    const user = await api.login(credentials);
    setUser(user);
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// 使用
function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

---

## 五、组件模式完整示例

### 容器/展示分离
```typescript
// Container: 负责数据获取
function UserListContainer() {
  const { data: users, isLoading, error } = useUsers();
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  return <UserList users={users} />;
}

// Presentational: 纯 UI
interface UserListProps { users: User[]; }
function UserList({ users }: UserListProps) {
  return (
    <ul>
      {users.map(user => <UserListItem key={user.id} user={user} />)}
    </ul>
  );
}
```

### Compound Components（Tabs）
```typescript
interface TabsContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextType | null>(null);

function Tabs({ children, defaultTab }: { children: React.ReactNode; defaultTab: string }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

function Tab({ value, children }: { value: string; children: React.ReactNode }) {
  const { activeTab, setActiveTab } = useContext(TabsContext)!;
  return (
    <button
      className={`tab ${activeTab === value ? 'active' : ''}`}
      onClick={() => setActiveTab(value)}
    >
      {children}
    </button>
  );
}

function TabPanel({ value, children }: { value: string; children: React.ReactNode }) {
  const { activeTab } = useContext(TabsContext)!;
  if (activeTab !== value) return null;
  return <div className="tab-panel">{children}</div>;
}

// 使用
<Tabs defaultTab="tab1">
  <Tab value="tab1">Tab 1</Tab>
  <Tab value="tab2">Tab 2</Tab>
  <TabPanel value="tab1">Content 1</TabPanel>
  <TabPanel value="tab2">Content 2</TabPanel>
</Tabs>
```

---

## 六、性能优化完整示例

### 代码分割
```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

### 虚拟滚动
```typescript
import { FixedSizeList } from 'react-window';

function VirtualList({ items }: { items: Item[] }) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <ItemRow item={items[index]} />
    </div>
  );
  return (
    <FixedSizeList height={600} itemCount={items.length} itemSize={80} width="100%">
      {Row}
    </FixedSizeList>
  );
}
```

---

## 七、样式方案完整示例

### CSS Module
```typescript
// Button.module.css
.button { padding: 8px 16px; border-radius: 4px; cursor: pointer; }
.primary { background-color: #007bff; color: white; }

// Button.tsx
import styles from './Button.module.css';
function Button({ variant = 'primary', children }: ButtonProps) {
  return <button className={`${styles.button} ${styles[variant]}`}>{children}</button>;
}
```

### Tailwind CSS
```typescript
function Button({ children, variant = 'primary' }: ButtonProps) {
  const variantClasses = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-500 text-white hover:bg-red-600',
  };
  return (
    <button className={`px-4 py-2 rounded font-medium transition-colors ${variantClasses[variant]}`}>
      {children}
    </button>
  );
}
```

---

## 八、错误处理完整示例

### Error Boundary
```typescript
interface ErrorBoundaryProps { children: React.ReactNode; fallback?: React.ReactNode; }
interface ErrorBoundaryState { hasError: boolean; error: Error | null; }

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong</div>;
    }
    return this.props.children;
  }
}
```

---

## 九、React 19 新特性示例

### use() Hook
```typescript
// 直接读取 Promise，无需 useEffect + useState
function CommentsPage({ commentsPromise }: { commentsPromise: Promise<Comment[]> }) {
  const comments = use(commentsPromise);
  return (
    <ul>
      {comments.map(c => <li key={c.id}>{c.text}</li>)}
    </ul>
  );
}
// 配合 Suspense 使用
<Suspense fallback={<Loading />}>
  <CommentsPage commentsPromise={fetchComments()} />
</Suspense>
```

### ref 作为 prop（不再需要 forwardRef）
```typescript
// React 19: 直接接收 ref
function TextInput({ ref, label }: { ref: React.Ref<HTMLInputElement>; label: string }) {
  return <input ref={ref} placeholder={label} />;
}

// 旧方式（React 18）
const TextInput = forwardRef<HTMLInputElement, { label: string }>((props, ref) => {
  return <input ref={ref} placeholder={props.label} />;
});
```

### useActionState + 表单
```typescript
async function createTodo(formData: FormData) {
  const title = formData.get('title') as string;
  await api.createTodo({ title });
}

function TodoForm() {
  const [state, formAction, isPending] = useActionState(createTodo, null);
  return (
    <form action={formAction}>
      <input name="title" />
      <button disabled={isPending}>Add Todo</button>
    </form>
  );
}
```
