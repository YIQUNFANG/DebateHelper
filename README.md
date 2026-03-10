# Debate Engine

多智能体论证分析与回复生成 CLI 工具。

## 安装

```bash
pip install .
```

## 使用方法

### 交互模式（推荐）

```bash
debate-engine --api-key sk-your-key
```

程序会依次提示输入背景、对方消息和目标，支持多轮对话。

### 单次模式

```bash
debate-engine --api-key sk-xxx \
  --context "我发了一个求婚视频" \
  --message "倒贴，廉价" \
  --goal burn
```

### 使用环境变量

```bash
export API_KEY=sk-xxx
export MODEL_NAME=gpt-4o
debate-engine
```

### 使用 .env 文件

```bash
cp .env.example .env  # 编辑填入密钥
debate-engine
```

### 兼容本地模型

```bash
# Ollama
debate-engine --base-url http://localhost:11434/v1 --api-key ollama --model llama3

# LM Studio
debate-engine --base-url http://localhost:1234/v1 --api-key lm-studio --model local-model
```

### 也可以这样运行

```bash
python -m debate_engine --api-key sk-xxx
```

## CLI 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--base-url` | OpenAI 兼容 API 地址 | `$API_BASE_URL` 或 `https://api.openai.com/v1` |
| `--api-key` | API 密钥 | `$API_KEY` |
| `--model` | 模型名称 | `$MODEL_NAME` 或 `gpt-4o` |
| `-c, --context` | 对话背景（单次模式） | — |
| `-m, --message` | 对方消息（单次模式） | — |
| `-g, --goal` | 目标：`debate`/`de-escalate`/`burn` 或 `1`/`2`/`3` | — |

## 架构

```
用户输入 ──► [分析师] ──┐
                        ├──► [战术师] ──► [文案师] ──► 3 级回复
           [逻辑师] ──┘
            (并行)
```

| 智能体 | 角色 | 执行方式 |
|--------|------|----------|
| 分析师 | 心理情报 — 动机、触发点、不安全感 | 并行 |
| 逻辑师 | 结构情报 — 谬误、无效前提 | 并行 |
| 战术师 | 战略综合 — 融合心理+逻辑生成作战计划 | 顺序 |
| 文案师 | 语言情报 — 生成三级强度回复 | 顺序 |

## 会话历史

每次运行会创建一个临时历史文件，记录每轮的输入、分析和回复。后续轮次的智能体会接收前几轮的完整上下文，使分析更连贯。程序退出时历史文件自动删除。

## 科学基础

- **归因理论** (Heider, 1958; Kelley, 1967)
- **形式逻辑与谬误分类** (Aristotle; Hamblin, 1970)
- **社会交换理论** (Homans, 1958; Blau, 1964)
- **自恋创伤框架** (Kohut, 1971)
