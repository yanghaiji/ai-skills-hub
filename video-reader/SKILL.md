---
name: video-reader
description: 解析视频文件内容：提取元信息、抽帧关键画面、语音转文字（faster-whisper）。先总结视频表达的核心内容告知用户，再根据用户需求做后续操作。触发条件：用户要求解析、理解、总结视频，或基于视频内容继续完成任务时。支持 mp4/mov/avi/mkv/flv/wmv/webm。
metadata:
  author: Yanghaiji
  version: "1.0.0"
---

# Video Reader

通过 ffmpeg + faster-whisper 解析视频文件，**先输出核心内容总结，再根据用户需求继续后续操作**。

## 依赖检查

所有脚本会自动探测 ffmpeg/ffprobe（PATH 优先，再兜底 winget/常见安装目录）。若缺失，脚本会提示可运行安装脚本：

```bash
python <skill_dir>/scripts/install_ffmpeg.py   # Windows 走 winget，macOS 走 brew
```

> ⚠️ **安装是有副作用的操作，必须先征得用户同意后再执行**。安装后无需重启终端，脚本即可命中。

语音转文字额外依赖（缺失时提示用户安装）：

```bash
pip install faster-whisper   # 语音转文字需要（首次运行会自动下载模型）
```

> whisper 模型下载默认走 `hf-mirror.com` 镜像（脚本内置，国内可用）；如需其他来源，设置环境变量 `HF_ENDPOINT` 覆盖。

## Skill 脚本路径

所有脚本位于本 Skill 目录下的 `scripts/` 子目录。

> `<skill_dir>` 代表本 SKILL.md 所在目录的绝对路径，调用时替换为实际路径。

## 脚本一览

| 脚本 | 用途 | 适用场景 |
|------|------|----------|
| `extract_info.py` | 提取元信息（时长、分辨率、音轨等） | **第一步必执行**，评估解析策略 |
| `transcribe_audio.py` | 语音转文字（带时间戳） | 视频有口播/讲解时，**核心内容主要来源** |
| `extract_frames.py` | 按间隔抽取关键帧为 PNG | 理解画面内容（由 AI 直接读取图片分析） |
| `install_ffmpeg.py` | 自动安装 ffmpeg（winget/brew） | **检测到 ffmpeg 缺失且用户同意后**执行 |
| `ffmpeg_env.py` | 共享：工具探测 + 缺失提示 | 内部模块，无需直接调用 |

## 使用方式

### 1. 提取元信息

```bash
python <skill_dir>/scripts/extract_info.py "<video_path>"
```

输出 JSON：时长、分辨率、帧率、视频/音频编码、是否有音轨。**根据时长决定后续策略**。

### 2. 语音转文字

```bash
python <skill_dir>/scripts/transcribe_audio.py "<video_path>" [--model small] [--language zh] [--output result.txt]
```

- `--model`：whisper 模型大小，`tiny | base | small | medium | large-v3`，默认 `small`（中文效果好）。时长 >30 分钟可用 `base` 提速
- `--language`：语言提示，如 `zh`、`en`；不填则自动检测
- 输出带时间戳的分段文本 + 全文

### 3. 抽取关键帧

```bash
python <skill_dir>/scripts/extract_frames.py "<video_path>" [--max-frames 8] [--output-dir DIR]
```

- 默认按时长自动均匀抽帧（最多 8 帧），输出每帧 PNG 的绝对路径及对应时间点
- **抽取后必须用 Read 工具逐张读取这些 PNG**，分析画面内容（文字、图表、场景、操作演示）

## 自动发现视频

当用户未指定路径时，按以下顺序扫描（仅匹配当前目录、不递归）：

1. 用户当前打开文件所在目录
2. 项目根目录下的 `videos/`、`docs/`、`media/` 子目录

查找所有 `.mp4 .mov .avi .mkv .flv .wmv .webm` 文件，多个则列出供用户选择。

## 工作流程（必须遵守）

```
阶段零：环境准备
- [ ] Step 0: 任一脚本报"未找到 ffmpeg" → 询问用户是否自动安装，同意后运行 install_ffmpeg.py

阶段一：内容解析
- [ ] Step 1: 定位视频文件，运行 extract_info.py 了解时长/音轨
- [ ] Step 2: 有音轨 → 运行 transcribe_audio.py 获取讲解文本
- [ ] Step 3: 运行 extract_frames.py 抽帧，用 Read 工具读取图片分析画面
- [ ] Step 4: 交叉印证语音与画面，形成完整理解

阶段二：报告核心内容（先完成这一步，才能做别的）
- [ ] Step 5: 按下方模板输出【视频核心内容】总结，明确告知用户

阶段三：按需继续
- [ ] Step 6: 根据用户的后续需求（写代码/写文档/提建议/整理笔记等），
             基于已解析的内容继续完成
```

> 若用户在同一条消息里已说明后续需求，Step 5 汇报核心内容后**直接继续**执行 Step 6，无需等待确认。

## 核心内容总结模板

```markdown
## 📹 视频核心内容

**基本信息**：时长 X 分钟 | 分辨率 | 是否含语音讲解

**主题**：一句话概括视频表达的核心内容

**要点**：
1. [按时间线或逻辑归纳的关键信息点]
2. ...

**画面/语音摘要**：（简述讲解脉络 + 关键画面内容）

以上是我对这个视频的理解，接下来我可以帮你：...（结合用户诉求给出建议）
```

## 注意事项

- **路径含空格/中文/括号**：必须用引号包裹
- **超长视频**（>1 小时）：先与用户确认是否全量转写，或指定时间段（`--start`/`--end`）
- **无音轨视频**（如监控、纯画面录屏）：跳过转写，仅靠抽帧分析
- **首次转写需下载模型**（脚本默认走 hf-mirror 镜像）：失败时提示用户网络问题，可降级 `--model tiny` 重试
- **隐私提示**：转写与抽帧的临时文件在系统临时目录，不会写入项目仓库
- **模型内存不足报错**：降级使用更小的模型（tiny/base）
