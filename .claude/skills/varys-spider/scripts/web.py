#!/usr/bin/env python3
"""web.py - Manage Varys Spider's intelligence network (web.json)

Single source of truth for:
- DEFAULT_WEB structure
- load/save helpers
- enable/disable commands

"""

import json
import sys
from pathlib import Path

WEB_PATH = Path.home() / ".openclaw/varys-spider/web.json"

DEFAULT_WEB = {
    "network": {
        "little_birds": {
            "twitter": {"enabled": False, "requires": ["AUTH_TOKEN", "CT0"]},
            "reddit": {"enabled": False, "requires": ["REDDIT_CLIENT_ID", "REDDIT_SECRET"]},
            "hackernews": {"enabled": True, "requires": [], "min_score": 100},
        },
        "citadel": {
            "rss": {
                "enabled": True,
                "requires": [],
                "feeds": [
                    {"name": "Reuters", "url": "http://feeds.reuters.com/reuters/topNews"},
                    {"name": "BBC", "url": "http://feeds.bbci.co.uk/news/rss.xml"},
                    {"name": "AP", "url": "https://apnews.com/hub/rss"},
                ],
            },
            "newsapi": {"enabled": False, "requires": ["NEWSAPI_KEY"], "queries": ["technology", "world"]},
            "techmeme": {"enabled": True, "requires": [], "url": "https://techmeme.com"},
        },
        "underworld": {
            "github": {"enabled": True, "requires": [], "since": "daily"},
            "arxiv": {"enabled": False, "requires": [], "query": "cat:cs.AI", "max_results": 10},
            "producthunt": {"enabled": False, "requires": ["PRODUCTHUNT_TOKEN"]},
        },
    },
    "intelligence_preferences": {
        "tongue": "zh",
        "verbosity": "measured",
        "scroll_length": 10,
        "hours_of_history": 24,
        "timezone": "America/Los_Angeles",
    },
}


def load_web():
    if WEB_PATH.exists():
        with open(WEB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(json.dumps(DEFAULT_WEB))


def save_web(web):
    WEB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(WEB_PATH, "w", encoding="utf-8") as f:
        json.dump(web, f, indent=2, ensure_ascii=False)


def show_web():
    web = load_web()
    print("🕷️  The Spider's Intelligence Network\n")
    for tier, sources in web.get("network", {}).items():
        print(f"{tier.replace('_', ' ').title()}:")
        for name, cfg in sources.items():
            status = "✅" if cfg.get("enabled") else "❌"
            req = cfg.get("requires") or []
            req_s = f" (needs: {', '.join(req)})" if (req and not cfg.get("enabled")) else ""
            print(f"  {status} {name}{req_s}")
        print()


def enable_source(name):
    web = load_web()
    for _, sources in web.get("network", {}).items():
        if name in sources:
            sources[name]["enabled"] = True
            save_web(web)
            print(f"✅ Enabled: {name}")
            return
    print(f"❌ Unknown source: {name}")


def disable_source(name):
    web = load_web()
    for _, sources in web.get("network", {}).items():
        if name in sources:
            sources[name]["enabled"] = False
            save_web(web)
            print(f"❌ Disabled: {name}")
            return
    print(f"❌ Unknown source: {name}")


def init_web():
    web = load_web()
    save_web(web)
    print(f"✅ Initialized: {WEB_PATH}")


def main():
    if len(sys.argv) < 2:
        show_web()
        return

    cmd = sys.argv[1]
    if cmd == "show":
        show_web()
    elif cmd == "init":
        init_web()
    elif cmd == "enable" and len(sys.argv) > 2:
        enable_source(sys.argv[2])
    elif cmd == "disable" and len(sys.argv) > 2:
        disable_source(sys.argv[2])
    else:
        print("Usage: varys-spider web [show|init|enable SOURCE|disable SOURCE]")


if __name__ == "__main__":
    main()
