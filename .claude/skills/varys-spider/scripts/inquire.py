#!/usr/bin/env python3
"""inquire.py - Keyword query across current collected intelligence.

This reads config.json, collects, filters, clusters, then filters clusters by keyword.

Usage:
  varys-spider query "moltbook"

"""

from __future__ import annotations

import sys

from config import load_config
from collect import (
    collect_rss,
    collect_hackernews,
    collect_github,
    collect_techmeme,
    collect_twitter,
)
from verify import cluster, filter_by_topics


def main():
    if len(sys.argv) < 2:
        print('Usage: varys-spider query "keyword"')
        sys.exit(1)

    q = " ".join(sys.argv[1:]).strip().lower()
    cfg = load_config()
    src = cfg.get("sources", {})

    items = []
    if src.get("rss", {}).get("enabled"):
        items += collect_rss(src.get("rss", {}))
    if src.get("techmeme", {}).get("enabled"):
        items += collect_techmeme(src.get("techmeme", {}))
    if src.get("hackernews", {}).get("enabled"):
        items += collect_hackernews(src.get("hackernews", {}))
    if src.get("github", {}).get("enabled"):
        items += collect_github(src.get("github", {}))
    if src.get("twitter", {}).get("enabled"):
        items += collect_twitter(src.get("twitter", {}))

    items = filter_by_topics(items, cfg.get("topics", {}))
    clusters = cluster(items)

    matched = []
    for c in clusters:
        blob = (c.get("title") or "") + " " + (c.get("url") or "")
        if q in blob.lower():
            matched.append(c)

    if not matched:
        print(f"No intelligence found for: {q}")
        return

    print(f"🕷️ Query results for: {q}\n")
    for c in matched[:20]:
        seal, label, conf = c["seal"]
        print(f"{seal} [{label}] ({int(conf*100)}%)")
        print(f"- {c['title']}")
        if c.get("sources"):
            print(f"- Sources: {', '.join(c['sources'])}")
        if c.get("url"):
            print(f"- Link: {c['url']}")
        print("")


if __name__ == "__main__":
    main()
