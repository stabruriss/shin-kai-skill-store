---
name: varys-spider
description: Generate hybrid intelligence briefings combining Twitter/X (via bird CLI) and Perplexity for multi-source news aggregation with Chinese audio summaries. Use when the user asks for "简报", "briefing", "情报简报", or automated news aggregation with Chinese audio output.
---

# Varys Spider

A hybrid intelligence briefing skill combining Twitter/X (via bird CLI) and Perplexity for multi-source news aggregation with Chinese audio summaries.

## Overview

Varys Spider generates bilingual (Chinese-focused) intelligence briefings with:
- **Audio summary** (Chinese TTS via Edge TTS) - sent FIRST
- **Text digest** with inline citations - sent AFTER audio

Data sources:
- **Bird (Twitter/X)**: Focus account monitoring via [bird CLI](https://github.com/steipete/bird) with cookie auth
- **Perplexity**: Real-time web search with prompt-driven queries (P1/P2/P3 priority), output in Chinese

## Features

- **Dual-source collection**: Twitter/X + Perplexity web search
- **Quality gates**: Signal scoring + Diversity gate + Trust level classification
- **Chinese-first output**: Audio narration and text in Chinese
- **Inline citations**: Sources attached to each item, not listed at end
- **Audio-first delivery**: TTS audio sent before text digest
- **Trust levels**: 5-tier credibility system (🏛️📊🔥💭🍺)
- **Time-aware queries**: Current timestamp added to Perplexity prompts to avoid duplicates
- **Source-specific prompts**: Perplexity searches prioritize Reddit, Hacker News, WSJ, Reuters, BBC, AP, The Economist

## Prerequisites

### 1. Install bird CLI

```bash
npm install -g @steipete/bird
```

Or use npx without installing:
```bash
npx @steipete/bird whoami
```

### 2. Get Twitter Cookies

1. Log in to x.com in your browser
2. Open DevTools (F12) → Application/Storage → Cookies
3. Copy `auth_token` and `ct0` values

### 3. Install Python Dependencies

```bash
pip3 install edge-tts requests
```

## Quick Start

```bash
# Set credentials
export BIRD_AUTH_TOKEN="your_auth_token_here"
export BIRD_CT0="your_ct0_cookie_here"
export OPENROUTER_API_KEY="sk-or-v1-your_key_here"

# Run a briefing
python3 scripts/main.py --edition morning --output both --target 8509139631
```

## Configuration

### Credentials (.env file)

Create `.env` in skill root:

```bash
# Twitter/X Web Cookie Auth (from browser dev tools)
BIRD_AUTH_TOKEN=your_auth_token_here
BIRD_CT0=your_ct0_cookie_here

# OpenRouter API Key for Perplexity
OPENROUTER_API_KEY=sk-or-v1-your_key_here
```

### Focus Accounts

Edit `scripts/config_loader.py` to customize:

```python
focus_accounts = [
    # AI/Tech
    "mranti", "wuyuesanren", "op7418", "dair_ai", "yetone",
    "steipete", "bcherny", "gregisenberg", "emollick",
    # Finance/Trading
    "WallStTV", "yriica", "fxtrader", "rryssf_",
    # Politics/Polling
    "CookPolitical", "FiveThirtyEight", "DecisionDeskHQ",
    "Redistrict", "gelliottmorris",
    # Mainstream Media
    "BBCWorld", "BBCBreaking", "Reuters", "WSJ",
    "nytimes", "TheEconomist",
    # Chinese Community
    "renfanzi", "dotey", "lifesinger", "vista8",
    "fanshimin", "superzen", "Alex8282019"
]
```

### Perplexity Prompts

Prompts are configured to:
- **Specify required sources**: Reddit, Hacker News, WSJ, Reuters, BBC, AP, The Economist
- **Require Chinese output**: "你的输出内容必须是中文"
- **Avoid Chinese media**: Unless China-specific events
- **Include current timestamp**: To avoid duplicate results

## Output Format

### Audio (Chinese TTS)

- Generated via Microsoft Edge TTS (free)
- Voice: zh-CN-XiaoxiaoNeural
- Max duration: 5 minutes
- Sent FIRST to Telegram

### Text Digest

Format per item:
```
—-

🐦 @username

——————————————————
可信度：📊 专业评论
——————————————————
[原文 - English]
{Tweet content}
——————————————————
[中文翻译]
(请将此部分翻译成中文)

来源 1: https://x.com/username/status/123456

————
```

## Architecture

```
Fetch (Bird CLI + Perplexity)
    ↓
Filter (deduplicate, exclude ads/sports/entertainment)
    ↓
Trust Level Classification (5-tier system)
    ↓
Signal Scoring (P1/P2/P3 + diversity gate)
    ↓
Format (text with inline citations + TTS script)
    ↓
Generate Audio (Edge TTS)
    ↓
Deliver (Audio FIRST → Text)
```

## Delivery Order

1. **Audio message** (as voice) - Chinese TTS summary
2. **Text digest** - Full content with inline citations (may split into multiple messages)

## Quality Gates

### Diversity Gate
- Single author ≤ 6 items
- ≥ 3 different signal tiers (P1/P2/P3)

### Signal Gate
- Average score ≥ 10
- Must have ≥ 1 P2 or P3 items

## File Structure

```
varys-spider/
├── SKILL.md                    # This file
├── config.yaml                 # Configuration
├── .env.example                # Credentials template
├── .gitignore
├── requirements.txt            # Python dependencies
├── test.sh                     # Quick test script
├── prompts/
│   ├── p1_ai_immigration.txt  # P1: AI+移民
│   ├── p2_politics.txt        # P2: 政治
│   └── p3_finance.txt         # P3: 金融
└── scripts/
    ├── main.py                 # Entry point
    ├── config_loader.py        # Config parser
    ├── fetch_bird.py           # Twitter/X via bird CLI
    ├── fetch_perplexity.py     # Perplexity search
    ├── filter.py               # Content filtering
    ├── trust_level.py          # Credibility classification
    ├── signal.py               # Scoring & gates
    ├── format.py               # Output formatting
    ├── audio.py                # TTS generation
    └── deliver.py              # Telegram delivery
```

## Dependencies

- Python 3.11+
- Node.js + npm (for bird CLI)
- edge-tts (Python TTS library)
- requests (HTTP library)

## License

MIT
