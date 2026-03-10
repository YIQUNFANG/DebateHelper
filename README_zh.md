Chinese | [English](README.md)

# DebateHelper

> *不只是回复 — 而是解除对方武装。*

DebateHelper 是一款多智能体命令行工具，专为解构有害沟通、识别逻辑谬误、生成战术性回应而设计。基于**社会心理学**与**形式逻辑**，它将原始冲突转化为结构化分析，让你在任何语言或数字对抗中占据上风。

---

## 🧠 科学内核

不同于通用 AI 对话，DebateHelper 采用由专业智能体组成的**"智囊团"**，通过三个维度处理人际冲突：

**社会心理学** — 运用归因理论（Heider, 1958; Kelley, 1967）和自恋伤害检测（Kohut, 1971）解码对手的隐藏动机——从权力追求到不安全感驱动的攻击——并映射其情绪触发点、深层不安全感和沟通模式。

**形式逻辑** — 自动化的"逻辑审计员"，扫描 20 余种常见谬误，包括人身攻击、稻草人、滑坡谬误、循环论证、诉诸传统、移动门柱等。每个谬误都精确定位到犯错的原文引用。

**战术修辞** — 将心理"软肋"与逻辑"硬伤"综合为可执行的作战计划，产出的回应不只是回复——而是解除武装。

---

## 🛠️ 核心功能

### 多智能体编排
四个专业 AI 智能体作为协调智囊团工作。分析师和逻辑师**并行**运行以提高速度，随后战术师和文案师**顺序**执行以综合输出。

```
用户输入 ──► [分析师 🔬] ──┐
                            ├──► [战术师 🎯] ──► [文案师 ✍️] ──► 3 条回应
           [逻辑师 📐] ──┘
            (并行)          (顺序)            (顺序)
```

| 智能体 | 角色 | 技能 |
|--------|------|------|
| **分析师** 🔬 | 心理情报 | 归因理论、自恋伤害检测 |
| **逻辑师** 📐 | 结构情报 | 形式逻辑、谬误分类学 |
| **战术师** 🎯 | 战略情报 | 社会交换理论、战术综合 |
| **文案师** ✍️ | 语言情报 | 说服性沟通、冲突修辞 |

### 三级作战模式
每次分析生成三个不同强度的回应选项——选择适合你场景的：

| 等级 | 名称 | 使用场景 |
|------|------|----------|
| 🩺 **手术刀** | 精准降温 | 职业场合、个人边界、公众形象重要时 |
| 🛡️ **坦克** | 逻辑碾压 | 公开辩论、评论区、想要教育对方时 |
| ☢️ **核弹** | 痛点打击 | 对方越线时。仅限自卫。谨慎使用。 |

### 多轮上下文记忆
DebateHelper 跨轮次追踪整个对话。每次新分析都建立在之前的轮次之上——它记得对手之前说了什么、犯了哪些谬误、以及论点如何转移。智能体随着每一轮变得更聪明。

- 启动时自动创建会话历史文件
- 所有先前轮次注入智能体上下文，实现连贯的多轮分析
- 退出时自动删除历史文件——不留痕迹

### 隐私优先 & BYOK
**"自带密钥"** 架构。你的私人对话永远不会经过我们的服务器——它们只在你和你的 LLM 提供商之间。

- 支持**任何 OpenAI 兼容 API**：OpenAI、Gemini、Ollama、LM Studio、Azure 等
- API 密钥通过 CLI 参数、环境变量或 `.env` 文件提供
- 零遥测、零数据收集

### 双语支持 (中文 / English)
DebateHelper 原生支持中英双语——UI 提示、分析报告和生成的回应都会适配你的语言设置。

- 自动从系统语言环境检测（或通过 `--lang` 手动设置）
- `--lang zh` — 中文界面 + 中文智能体输出
- `--lang en` — 英文界面 + 英文智能体输出
- `--lang auto` — 从系统语言环境检测（默认）

### 极客终端 UI
由 [Rich](https://github.com/Textualize/rich) 驱动的精美彩色终端界面：

- 每个管道阶段的实时旋转加载反馈
- 每个回应等级的彩色面板（绿 / 蓝 / 红）
- 结构化分析报告，含心理画像、谬误表格和作战计划
- 轮次指示器和历史徽章

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/YIQUNFANG/DebateHelper.git && cd DebateHelper
pip install .
```

### 运行（交互模式 — 推荐）

```bash
debate-engine --api-key sk-your-key --lang zh
```

CLI 将引导你完成每一轮：背景 → 对手消息 → 目标 → 分析 → 3 条回应。输入 `y` 继续在同一线程中分析后续消息。

### 运行（一次性模式）

```bash
debate-engine \
  --api-key sk-xxx \
  --lang zh \
  --context "我发了一篇文章，收到了一条恶意评论" \
  --message "根本没人看你写的东西，笑死" \
  --goal burn

# English interface
debate-engine \
  --api-key sk-xxx \
  --context "I posted an article and got a hostile comment" \
  --message "Nobody even reads this, lmao" \
  --goal burn
```

### 通过 `python -m` 运行

```bash
python -m debate_engine --api-key sk-xxx --lang zh
```

---

## ⚙️ 配置

DebateHelper 按以下优先级解析配置：**CLI 参数 > 环境变量 > `.env` 文件 > 交互提示**。

### CLI 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--base-url` | OpenAI 兼容 API 端点 | `$API_BASE_URL` 或 `https://api.openai.com/v1` |
| `--api-key` | API 密钥 | `$API_KEY` 或交互式输入 |
| `--model` | 模型名称 | `$MODEL_NAME` 或 `gpt-4o` |
| `-c, --context` | 对话背景（一次性模式） | — |
| `-m, --message` | 对手的消息（一次性模式） | — |
| `-g, --goal` | 目标：`debate` / `de-escalate` / `burn` 或 `1` / `2` / `3` | — |
| `--lang` | UI 语言：`zh` / `en` / `auto` | `auto`（从系统语言检测） |

### 环境变量

```bash
export API_BASE_URL=https://api.openai.com/v1
export API_KEY=sk-your-key
export MODEL_NAME=gpt-4o
debate-engine --lang zh
```

### `.env` 文件

```bash
cp .env.example .env
# 编辑 .env 填入你的凭据
debate-engine --lang zh
```

---

## 🔌 LLM 兼容性

DebateHelper 支持**任何 OpenAI 兼容 API**：

```bash
# OpenAI
debate-engine --api-key sk-xxx --model gpt-4o --lang zh

# Google Gemini
debate-engine \
  --base-url https://generativelanguage.googleapis.com/v1beta/openai/ \
  --api-key YOUR_GEMINI_KEY \
  --model gemini-2.5-flash \
  --lang zh

# Ollama（本地）
debate-engine --base-url http://localhost:11434/v1 --api-key ollama --model llama3 --lang zh

# LM Studio（本地）
debate-engine --base-url http://localhost:1234/v1 --api-key lm-studio --model local-model --lang zh
```

---

## 📚 科学基础

| 理论 | 在 DebateHelper 中的应用 |
|------|--------------------------|
| **归因理论**（Heider, 1958; Kelley, 1967） | 解码对手的攻击性源于内在性格还是情境因素。识别其推理中的基本归因错误。 |
| **自恋伤害框架**（Kohut, 1971） | 映射驱动敌意沟通的心理脆弱性和自我保护机制。 |
| **形式谬误分类学**（Aristotle; Hamblin, 1970） | 系统检测 20 余种非形式谬误，附精确引文证据。 |
| **社会交换理论**（Homans, 1958; Blau, 1964） | 将冲突框架为成本/收益谈判，以识别最优策略行动。 |
| **自我决定理论**（Deci & Ryan, 1985） | 分析对手未满足的自主性、胜任感和关系需求如何表现为攻击性。 |

---

## 📄 许可证

MIT
