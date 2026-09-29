# React + TypeScript 常用代码模板

---

## 组件模板

### 基础组件
```typescript
interface ComponentProps {
  children?: React.ReactNode;
  className?: string;
}

function Component({ children, className }: ComponentProps) {
  return <div className={className}>{children}</div>;
}

export default Component;
```

### 带事件和状态的组件
```typescript
interface UserCardProps {
  user: User;
  showEmail?: boolean;
  onSelect?: (userId: number) => void;
}

function UserCard({ user, showEmail = true, onSelect }: UserCardProps) {
  return (
    <div onClick={() => onSelect?.(user.id)}>
      <h3>{user.name}</h3>
      {showEmail && <p>{user.email}</p>}
    </div>
  );
}

export default UserCard;
```

### 多文件组件结构
```
Button/
├── Button.tsx          # 组件实现
├── Button.types.ts     # Props 类型定义
├── Button.styles.ts    # 样式（如使用 CSS-in-JS）
├── Button.test.tsx     # 测试
├── Button.module.css   # CSS Module（如使用）
└── index.ts            # 统一导出
```

---

## Hook 模板

### 数据获取 Hook
```typescript
import { useQuery } from '@tanstack/react-query';

function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await fetch('/api/users');
      if (!res.ok) throw new Error('Failed to fetch users');
      return res.json() as Promise<User[]>;
    },
    staleTime: 5 * 60 * 1000, // 5 分钟
  });
}
```

### 防抖 Hook
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

### 本地存储 Hook
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

---

## 测试模板

### 组件测试
```typescript
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import Component from './Component';

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component>Content</Component>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('handles click', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    render(<Component onClick={handleClick}>Click me</Component>);
    await user.click(screen.getByRole('button', { name: /click me/i }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Hook 测试
```typescript
import { renderHook, act } from '@testing-library/react';

describe('useCounter', () => {
  it('increments count', () => {
    const { result } = renderHook(() => useCounter(0));
    act(() => { result.current.increment(); });
    expect(result.current.count).toBe(1);
  });
});
```

### 集成测试（含 MSW Mock）
```typescript
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.get('/api/users', () => HttpResponse.json([{ id: 1, name: 'John' }])),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserList', () => {
  it('loads and displays users', async () => {
    render(<UserList />);
    expect(await screen.findByText('John')).toBeInTheDocument();
  });
});
```

---

## 工程化配置模板

### ESLint 配置
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
    "plugin:react/jsx-runtime"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "react-hooks/exhaustive-deps": "warn",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
```

### Prettier 配置
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "always"
}
```

### tsconfig.json 关键配置
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "jsx": "react-jsx",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```
