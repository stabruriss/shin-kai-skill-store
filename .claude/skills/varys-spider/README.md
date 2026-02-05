# Varys Spider v1.0 - Final

Hybrid intelligence briefing skill with auto-translation and Pacific Time.

## Requirements

- Node.js + npm (for bird CLI)
- Python 3.11+
- pip packages: edge-tts, requests

## Setup

```bash
# Install bird CLI
npm install -g @steipete/bird

# Install Python dependencies
pip3 install edge-tts requests --break-system-packages

# Configure credentials
cp .env.example .env
# Edit .env with your Twitter cookies and OpenRouter key
```

## Run

```bash
python3 scripts/main.py --edition morning --output both --target YOUR_CHAT_ID
```

## Features

- **Bird (Twitter)**: 2 tweets per account, auto-translated to Chinese
- **Perplexity**: P1/P2/P3 topics, English sources prioritized
- **Time**: Pacific Time (PST/PDT)
- **Audio**: ~5 min max, cleaned markdown
- **Delivery**: Audio first, then 2-3 text messages

## Files

- `scripts/fetch_bird.py` - Twitter via bird CLI
- `scripts/fetch_perplexity.py` - Perplexity search
- `scripts/format.py` - Formatting with auto-translation
- `scripts/translate.py` - OpenRouter translation
- `scripts/deliver.py` - Telegram delivery
