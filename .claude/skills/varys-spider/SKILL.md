---
name: varys-spider
description: Multi-source intelligence briefing skill (RSS, Twitter/X via bird, Hacker News, GitHub Trending, Techmeme) with credibility seals, durable user configuration (language, source mix/quotas, focus accounts, topics), and durable feedback recording (feedback.json) enabling optional long-run learning. Varys speaks as a spider with eyes and ears throughout the realm.
---

# 🕷️ Varys Spider

*"The Spider has his eyes and ears throughout the realm. I bring you what is known, what is suspected, and what is mere tavern gossip."*

## ⚠️ First Time Setup - The Spider's Network

When this skill loads, the agent MUST verify available intelligence sources and guide setup.

### Prerequisites Check

Run: `varys-spider --check-network`

**Core Tools (Required):**
- [ ] `python3` 3.8+ - For running the Spider's scripts
- [ ] `curl` or `wget` - For web requests

**Information Sources (Enable what you can):**

#### Tier 1: Little Birds (Social Media)
| Source | Cost | Auth Required | Priority |
|--------|------|---------------|----------|
| Twitter/X (bird) | Free | ✅ AUTH_TOKEN, CT0 | High |
| Reddit API | Free | ✅ Reddit app | Medium |
| Hacker News API | **FREE** | ❌ No auth | High |

#### Tier 2: The Citadel (News)
| Source | Cost | Auth Required | Priority |
|--------|------|---------------|----------|
| RSS Feeds (Reuters, BBC) | **FREE** | ❌ No auth | High |
| NewsAPI | Free tier | ✅ API Key | Medium |
| Techmeme | **FREE** | ❌ Scraping | Medium |

#### Tier 3: The Underworld (Niche)
| Source | Cost | Auth Required | Notes |
|--------|------|---------------|-------|
| GitHub Trending | **FREE** | ❌ No auth | Tech/dev focus |
| arXiv API | **FREE** | ❌ No auth | Research papers |
| Product Hunt | Free tier | ✅ Token | Product launches |

### Minimal Setup (Works Immediately)
```bash
# Just these - all FREE, no auth required:
# - RSS feeds (Reuters, BBC, AP)
# - Hacker News API
# - GitHub Trending
# - Techmeme scraping
```

### Recommended Setup
```bash
# Plus these for better coverage:
# - Twitter (bird CLI + credentials)
# - NewsAPI (free tier, 100 req/day)
```

### Full Network
```bash
# All sources configured
```

## 🎭 Commands

```bash
# Setup / health
varys-spider --check-network            # Check available sources
varys-spider init                       # Create ~/.openclaw/varys-spider/config.json + feedback.json

# Daily intelligence
varys-spider report                     # Generate briefing (reads config.json)

# Queries
varys-spider query "moltbook"           # On-demand keyword query (respects config)

# Configuration (durable; no need to repeat preferences every time)
varys-spider config get output
varys-spider config set output.language '"zh"'
varys-spider config set mix.twitter 8
varys-spider config set sources.twitter.focus_accounts '["openclaw","moltbook"]'
varys-spider config add-topic cybersecurity
varys-spider config remove-source twitter

# Feedback (durable; enables optional long-run learning)
varys-spider whisper "4 Moltbook那条置信度应该更低"
varys-spider feedback show

# Legacy network manager (web.json). config.json is the primary interface now.
varys-spider web show
```

### Configuration Files
- `~/.openclaw/varys-spider/config.json` — language, mix/quotas, focus accounts, topics
- `~/.openclaw/varys-spider/feedback.json` — user feedback log for later analysis

### Twitter/X Note
Twitter collection is supported via `bird`, but secrets are **not stored** in config.
Set `AUTH_TOKEN` and `CT0` in environment when running/cron.


## 📡 Intelligence Seals

| Seal | Meaning | Confidence |
|------|---------|------------|
| 🟣 **Spider's Web** | 3+ authoritative sources | 90%+ |
| 🔵 **The Citadel** | Reputable news outlet | 75-89% |
| 🟢 **Little Birds** | Aggregated social intel | 60-74% |
| 🟡 **Tavern Whispers** | Single social source | <60% |
| 🔴 **The Dungeons** | Unverified rumor | Flag |

*"Knowledge is power, but verified knowledge is true power."* — Varys
