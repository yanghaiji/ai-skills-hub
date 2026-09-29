# 模板

## SKILL.md 模板

```markdown
---
name: {skill-name}
description: "{description}. Use when {trigger-context}. Do not use when {negative-context}. Triggers: {trigger-phrases}."
compatibility: {compatibility}
license: {license}
allowed-tools: {allowed-tools}
metadata:
  author: {author}
  version: "1.0.0"
---

# {Skill Title}

{One paragraph overview}

## 何时使用

- {use case 1}
- {use case 2}

## 何时不使用

- {negative case 1}

## Setup

{Prerequisites and installation}

## Usage

{How to use the skill}

## 验证

- [ ] {check 1}
- [ ] {check 2}

## References

- `references/{file}.md`
```

## Python 脚本模板

```python
#!/usr/bin/env python3
"""Script description."""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="...")
    args = parser.parse_args()
    print("Hello from {skill-name}")

if __name__ == "__main__":
    main()
```

## Node.js 脚本模板

```javascript
#!/usr/bin/env node
/** Script description */

function main() {
  console.log('Hello from {skill-name}');
}

main();
```

## Bash 脚本模板

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Hello from {skill-name}"
```