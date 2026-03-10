# DebateHelper

> *Don't just reply — disarm.*

DebateHelper is a multi-agent command-line tool designed to deconstruct toxic communication, identify logical fallacies, and generate tactical responses. Grounded in **Social Psychology** and **Formal Logic**, it transforms raw conflict into structured analysis, giving you the upper hand in any verbal or digital confrontation.

---

## 🧠 The Scientific Core

Unlike generic AI chat, DebateHelper employs a **"Think Tank"** of specialized agents to process human conflict through three distinct lenses:

**Social Psychology** — Utilizes Attribution Theory (Heider, 1958; Kelley, 1967) and Narcissistic Injury Detection (Kohut, 1971) to decode the opponent's hidden motives — from power-seeking to insecurity-driven aggression — and map their emotional triggers, deep insecurities, and communication patterns.

**Formal Logic** — An automated "Logic Auditor" that scans for 20+ common fallacies including Ad Hominem, Strawman, Slippery Slope, Circular Reasoning, Appeal to Tradition, Moving the Goalposts, and more. Every fallacy is pinned to the exact quote that commits it.

**Tactical Rhetoric** — Synthesizes psychological "soft spots" with logical "hard errors" into an actionable Battle Plan, producing responses that don't just reply — they disarm.

---

## 🛠️ Key Features

### Multi-Agent Orchestration
Four specialized AI agents work as a coordinated think tank. The Analyst and Logician run **in parallel** for speed, then the Tactician and Copywriter execute **sequentially** to synthesize and produce output.

```
User Input ──► [Analyst 🔬] ──┐
                               ├──► [Tactician 🎯] ──► [Copywriter ✍️] ──► 3 Responses
              [Logician 📐] ──┘
               (parallel)        (sequential)          (sequential)
```

| Agent | Role | Skill |
|-------|------|-------|
| **The Analyst** 🔬 | Psychological Intelligence | Attribution Theory, Narcissistic Injury Detection |
| **The Logician** 📐 | Structural Intelligence | Formal Logic, Fallacy Taxonomy |
| **The Tactician** 🎯 | Strategic Intelligence | Social Exchange Theory, Tactical Synthesis |
| **The Copywriter** ✍️ | Linguistic Intelligence | Persuasive Communication, Conflict Rhetoric |

### Three-Tier Battle Mode
Every analysis generates three response options at different intensity levels — choose the one that fits your situation:

| Tier | Name | When to Use |
|------|------|-------------|
| 🩺 **The Surgeon** | Precision De-escalation | Professional settings, personal boundaries, public image matters |
| 🛡️ **The Tank** | Logic Crush | Public debates, comment sections, when you want to educate |
| ☢️ **The Nuclear** | Pain-Point Strike | When they crossed the line. Self-defense only. Use with caution. |

### Multi-Round Context Memory
DebateHelper tracks the entire conversation across rounds. Each new analysis builds on previous rounds — it remembers what the opponent said before, what fallacies they committed, and how they shifted their arguments. The agents get smarter with every round.

- Session history file created automatically on startup
- All prior rounds injected into agent context for coherent multi-turn analysis
- History file auto-deleted on exit — nothing persists

### Privacy-First & BYOK
**"Bring Your Own Key"** architecture. Your private conversations never touch our servers — they stay between you and your LLM provider.

- Works with **any OpenAI-compatible API**: OpenAI, Gemini, Ollama, LM Studio, Azure, and more
- API key provided via CLI flag, environment variable, or `.env` file
- Zero telemetry, zero data collection

### Geek-Centric Terminal UI
A beautiful, color-coded terminal interface powered by [Rich](https://github.com/Textualize/rich):

- Real-time spinner feedback during each pipeline phase
- Color-coded panels for each response tier (green / blue / red)
- Structured analysis report with psychological profile, fallacy table, and battle plan
- Round indicators and history badges

---

## 🚀 Quick Start

### Install

```bash
git clone <repo-url> && cd debate-engine
pip install .
```

### Run (Interactive Mode — Recommended)

```bash
debate-engine --api-key sk-your-key
```

The CLI will walk you through each round: background → opponent message → goal → analysis → 3 responses. Type `y` to continue analyzing follow-up messages in the same thread.

### Run (One-Shot Mode)

```bash
debate-engine \
  --api-key sk-xxx \
  --context "I posted an article and got a hostile comment" \
  --message "Nobody even reads this, lmao" \
  --goal burn
```

### Run with `python -m`

```bash
python -m debate_engine --api-key sk-xxx
```

---

## ⚙️ Configuration

DebateHelper resolves configuration in this priority order: **CLI flags > Environment variables > `.env` file > Interactive prompt**.

### CLI Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--base-url` | OpenAI-compatible API endpoint | `$API_BASE_URL` or `https://api.openai.com/v1` |
| `--api-key` | API key | `$API_KEY` or prompted interactively |
| `--model` | Model name | `$MODEL_NAME` or `gpt-4o` |
| `-c, --context` | Conversation background (one-shot mode) | — |
| `-m, --message` | Opponent's message (one-shot mode) | — |
| `-g, --goal` | Goal: `debate` / `de-escalate` / `burn` or `1` / `2` / `3` | — |

### Environment Variables

```bash
export API_BASE_URL=https://api.openai.com/v1
export API_KEY=sk-your-key
export MODEL_NAME=gpt-4o
debate-engine
```

### `.env` File

```bash
cp .env.example .env
# Edit .env with your credentials
debate-engine
```

---

## 🔌 LLM Compatibility

DebateHelper works with **any OpenAI-compatible API**:

```bash
# OpenAI
debate-engine --api-key sk-xxx --model gpt-4o

# Google Gemini
debate-engine \
  --base-url https://generativelanguage.googleapis.com/v1beta/openai/ \
  --api-key YOUR_GEMINI_KEY \
  --model gemini-2.5-flash

# Ollama (local)
debate-engine --base-url http://localhost:11434/v1 --api-key ollama --model llama3

# LM Studio (local)
debate-engine --base-url http://localhost:1234/v1 --api-key lm-studio --model local-model
```

---

## 📚 Scientific Foundations

| Theory | Application in DebateHelper |
|--------|----------------------------|
| **Attribution Theory** (Heider, 1958; Kelley, 1967) | Decodes whether the opponent's aggression stems from internal dispositions or situational factors. Identifies fundamental attribution errors in their reasoning. |
| **Narcissistic Injury Framework** (Kohut, 1971) | Maps psychological vulnerabilities and ego-protection mechanisms that drive hostile communication. |
| **Formal Fallacy Taxonomy** (Aristotle; Hamblin, 1970) | Systematic detection of 20+ informal fallacies with exact-quote evidence. |
| **Social Exchange Theory** (Homans, 1958; Blau, 1964) | Frames conflict as cost/reward negotiation to identify optimal strategic moves. |
| **Self-Determination Theory** (Deci & Ryan, 1985) | Analyzes opponent's unmet needs for autonomy, competence, and relatedness that manifest as aggression. |

---

## 📄 License

MIT
