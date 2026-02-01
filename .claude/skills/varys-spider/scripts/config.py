#!/usr/bin/env python3
"""config.py - Varys Spider configuration management.

Config is stored at:
  ~/.openclaw/varys-spider/config.json

Design goals:
- Single, durable config file for: language, source mix/quotas, focus accounts, topics.
- Safe defaults (works without auth; optional Twitter/NewsAPI/etc).

"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

STATE_DIR = Path.home() / ".openclaw" / "varys-spider"
CONFIG_PATH = STATE_DIR / "config.json"

DEFAULT_CONFIG = {
    "version": 1,
    "output": {
        "language": "zh",  # zh|en
        "max_items": 20,
        "ordering": "quota_then_confidence",  # quota_then_confidence|confidence_only
        "timezone": "America/Los_Angeles",
    },
    "mix": {
        "rss": 6,
        "hackernews": 4,
        "github": 2,
        "techmeme": 2,
        "twitter": 6,
    },
    "topics": {
        "include": [],
        "exclude": [],
    },
    "sources": {
        "rss": {
            "enabled": True,
            "feeds": [
                {"name": "Reuters", "url": "http://feeds.reuters.com/reuters/topNews"},
                {"name": "BBC", "url": "http://feeds.bbci.co.uk/news/rss.xml"},
                {"name": "AP", "url": "https://apnews.com/hub/rss"},
            ],
        },
        "hackernews": {"enabled": True, "min_score": 100},
        "github": {"enabled": True, "since": "daily"},
        "techmeme": {"enabled": True, "url": "https://techmeme.com"},
        "twitter": {
            "enabled": False,
            "max_items": 50,
            "focus_accounts": [],  # e.g. ["openclaw","moltbook"]
            "requires": ["AUTH_TOKEN", "CT0"],
        },
    },
}


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return deepcopy(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    ensure_state_dir()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def init_config() -> None:
    cfg = load_config()
    save_config(cfg)
    print(f"✅ Initialized: {CONFIG_PATH}")


def _get_path(obj: dict, path: str):
    cur = obj
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            raise KeyError(path)
        cur = cur[p]
    return cur


def _set_path(obj: dict, path: str, value):
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def cmd_get(path: str) -> None:
    cfg = load_config()
    val = _get_path(cfg, path)
    print(json.dumps(val, indent=2, ensure_ascii=False))


def cmd_set(path: str, json_value: str) -> None:
    cfg = load_config()
    value = json.loads(json_value)
    _set_path(cfg, path, value)
    save_config(cfg)
    print(f"✅ Set {path}")


def cmd_add_topic(topic: str) -> None:
    cfg = load_config()
    inc = cfg.setdefault("topics", {}).setdefault("include", [])
    if topic not in inc:
        inc.append(topic)
        save_config(cfg)
        print(f"✅ Added topic: {topic}")
    else:
        print(f"(already present) {topic}")


def cmd_remove_source(source: str) -> None:
    cfg = load_config()
    if source in cfg.get("sources", {}):
        cfg["sources"][source]["enabled"] = False
        save_config(cfg)
        print(f"✅ Disabled source: {source}")
    else:
        print(f"❌ Unknown source: {source}")


def main():
    if len(sys.argv) < 2:
        print("Usage: varys-spider config [init|get|set|add-topic|remove-source] ...")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init":
        init_config()
        return

    if cmd == "get" and len(sys.argv) >= 3:
        cmd_get(sys.argv[2])
        return

    if cmd == "set" and len(sys.argv) >= 4:
        cmd_set(sys.argv[2], " ".join(sys.argv[3:]))
        return

    if cmd == "add-topic" and len(sys.argv) >= 3:
        cmd_add_topic(" ".join(sys.argv[2:]).strip())
        return

    if cmd == "remove-source" and len(sys.argv) >= 3:
        cmd_remove_source(sys.argv[2])
        return

    print("Usage:")
    print("  varys-spider config init")
    print("  varys-spider config get topics")
    print("  varys-spider config set output.language \"\"zh\"\"")
    print("  varys-spider config add-topic cybersecurity")
    print("  varys-spider config remove-source twitter")
    sys.exit(1)


if __name__ == "__main__":
    main()
