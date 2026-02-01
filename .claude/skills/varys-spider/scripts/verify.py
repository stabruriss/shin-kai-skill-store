#!/usr/bin/env python3
"""verify.py - Credibility seals, clustering, and topic filtering.

NOTE: Confidence adjustments may consider feedback.json, but the magnitude is not
hardcoded; the calling agent decides how to interpret feedback.

"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

STATE_DIR = Path.home() / ".openclaw" / "varys-spider"
FEEDBACK_PATH = STATE_DIR / "feedback.json"


def load_feedback() -> dict:
    if FEEDBACK_PATH.exists():
        try:
            return json.loads(FEEDBACK_PATH.read_text("utf-8"))
        except Exception:
            return {}
    return {}


def normalize_title(t: str) -> str:
    t = (t or "").lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    stop = {"the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with"}
    toks = [w for w in t.split() if w not in stop]
    return " ".join(toks[:12])


def seal_for_cluster(items):
    tiers = {it.get("tier_hint") for it in items}
    sources = {it.get("source") for it in items}
    citadel = sum(1 for it in items if it.get("tier_hint") == "citadel")

    if citadel >= 2 and len(sources) >= 2:
        return "🌍", "Spider's Web", 0.9
    if citadel >= 1:
        return "📻", "The Citadel", 0.8
    if "little_birds" in tiers:
        return "📣", "Little Birds", 0.65
    if "tavern_whispers" in tiers:
        return "🍻", "Tavern Whispers", 0.45
    return "🧻", "The Dungeons", 0.2


def filter_by_topics(items: list[dict], topics: dict) -> list[dict]:
    inc = [t.lower() for t in (topics.get("include") or []) if t.strip()]
    exc = [t.lower() for t in (topics.get("exclude") or []) if t.strip()]

    def ok(it: dict) -> bool:
        text = (it.get("title") or "").lower() + " " + (it.get("url") or "").lower()
        if exc and any(x in text for x in exc):
            return False
        if inc:
            return any(x in text for x in inc)
        return True

    return [it for it in items if ok(it)]


def cluster(items: list[dict]) -> list[dict]:
    buckets = defaultdict(list)
    for it in items:
        key = normalize_title(it.get("title", ""))
        if not key:
            key = f"{it.get('kind','')}:{it.get('url','') or it.get('source','')}"
        buckets[key].append(it)

    clusters = []
    for _, its in buckets.items():
        seal = seal_for_cluster(its)
        rep = its[0]
        clusters.append({
            "seal": seal,
            "title": rep.get("title"),
            "url": rep.get("url"),
            "sources": sorted({it.get("source") for it in its if it.get("source")}),
            "kind": rep.get("kind"),
            "n": len(its),
        })

    clusters.sort(key=lambda c: (c["seal"][2], c["n"]), reverse=True)
    return clusters
