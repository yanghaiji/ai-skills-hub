# Test Case Generator

从需求文档自动生成测试用例、Python自动化测试代码和测试报告的skill。

## 功能特性

1. **多格式文档解析**：支持 .docx、.pdf、.md、.txt 格式的需求文档
2. **智能测试用例生成**：基于需求内容自动分析并生成测试用例
3. **自动化测试代码生成**：生成可直接运行的Python测试代码
4. **测试报告生成**：运行测试并生成详细的HTML测试报告

## 目录结构

```
test-case-generator/
├── SKILL.md                    # 主文档
├── README.md                   # 本文件
├── scripts/
│   ├── parse_document.py       # 文档解析脚本
│   ├── generate_test_cases.py  # 测试用例生成脚本
│   ├── generate_test_code.py   # Python测试代码生成脚本
│   ├── run_tests.py            # 测试运行和报告生成脚本
│   └── utils.py                # 工具函数
├── templates/
│   ├── README.md               # 模板说明
│   ├── test_case_template.json # 测试用例JSON模板
│   └── test_case_template.py   # 测试用例Python模板
└── references/
    ├── README.md               # 参考文档说明
    ├── test_patterns.md        # 测试模式参考
    ├── best_practices.md       # 测试最佳实践
    └── examples.md             # 测试用例示例
```

## 快速开始

### 1. 安装依赖

```bash
pip install python-docx pdfplumber pytest pytest-html
```

### 2. 使用流程

#### 步骤1：解析需求文档

```bash
python scripts/parse_document.py <需求文档路径> --output parsed_content.json
```

支持的文档格式：
- `.docx` - Word文档
- `.pdf` - PDF文档
- `.md` - Markdown文档
- `.txt` - 纯文本文档

#### 步骤2：生成测试用例

```bash
python scripts/generate_test_cases.py parsed_content.json --output test_cases.json
```

#### 步骤3：生成Python测试代码

```bash
python scripts/generate_test_code.py test_cases.json --output ./generated_tests
```

#### 步骤4：运行测试并生成报告

```bash
python scripts/run_tests.py ./generated_tests --report ./test_report.html
```

### 3. 完整工作流示例

```bash
# 解析需求文档
python scripts/parse_document.py requirements.docx -o parsed.json

# 生成测试用例
python scripts/generate_test_cases.py parsed.json -o test_cases.json

# 生成测试代码
python scripts/generate_test_code.py test_cases.json -o ./tests

# 运行测试并生成报告
python scripts/run_tests.py ./tests -r ./report.html
```

## 输出文件说明

### 测试用例文档 (test_cases.json)
包含所有生成的测试用例，结构如下：
- `test_cases`: 测试用例列表
- `summary`: 统计信息（总数、按优先级分类、按类型分类）

### Python测试代码 (generated_tests/)
```
generated_tests/
├── conftest.py          # pytest配置和fixtures
├── test_cases.py        # 测试用例代码
├── requirements.txt     # 依赖列表
└── README.md           # 使用说明
```

### 测试报告 (test_report.html)
HTML格式的测试报告，包含：
- 测试执行摘要
- 通过/失败统计
- 详细的测试结果
- 进度条可视化

## 高级用法

### 自定义测试模板

可以使用自定义模板生成测试代码：

```bash
python scripts/generate_test_code.py test_cases.json --template custom_template.py
```

### 批量处理

支持批量处理多个需求文档：

```bash
python scripts/parse_document.py doc1.docx doc2.pdf doc3.md -o all_content.json
```

### 集成到CI/CD

生成的测试代码可直接集成到CI/CD流程：

```yaml
# .github/workflows/test.yml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --html=report.html
```

## 测试用例类型

### 功能测试
验证系统功能是否按照需求正常工作。

### 边界测试
验证系统在边界条件下的行为，包括：
- 空值处理
- 最大/最小值
- 特殊字符
- 长度限制

### 异常测试
验证系统的异常处理能力，包括：
- 无效输入
- 网络错误
- 权限不足
- 资源不存在

## 注意事项

1. **文档格式**：确保需求文档格式清晰，包含明确的功能描述
2. **编码问题**：处理中文文档时确保UTF-8编码
3. **依赖管理**：首次使用需安装Python依赖
4. **测试环境**：确保测试环境与生产环境配置一致
5. **数据清理**：测试完成后清理测试数据

## 故障排除

### 文档解析失败
- 检查文件格式是否支持
- 确认文件未损坏
- 检查文件权限

### 测试代码生成错误
- 确认测试用例JSON格式正确
- 检查输出目录权限
- 查看错误日志

### 测试运行失败
- 检查pytest是否正确安装
- 确认测试代码语法正确
- 检查测试环境配置

## 参考资料

详细的测试模式和最佳实践请参考：
- `references/test_patterns.md` - 测试模式参考
- `references/best_practices.md` - 测试最佳实践
- `references/examples.md` - 测试用例示例

## 许可证

MIT License
