#!/usr/bin/env python3
"""feedback.py - Record user feedback for Varys Spider.

Feedback is stored at:
  ~/.openclaw/varys-spider/feedback.json

We record feedback durably, but we do NOT hardcode a numeric confidence demotion.
How to apply feedback is left to the agent's judgement at generation time.

"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

STATE_DIR = Path.home() / ".openclaw" / "varys-spider"
FEEDBACK_PATH = STATE_DIR / "feedback.json"


def _load() -> dict:
    if FEEDBACK_PATH.exists():
        return json.loads(FEEDBACK_PATH.read_text("utf-8"))
    return {}


def _save(obj: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    FEEDBACK_PATH.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", "utf-8")


def add_feedback(rating: int | None, comment: str, adjusted_topics=None, adjusted_sources=None):
    data = _load()
    day = datetime.utcnow().strftime("%Y-%m-%d")
    entry = {
        "at": datetime.utcnow().isoformat() + "Z",
        "rating": rating,
        "comment": comment,
        "adjusted_topics": adjusted_topics or [],
        "adjusted_sources": adjusted_sources or [],
    }
    data.setdefault(day, []).append(entry)
    _save(data)
    print(f"✅ Saved feedback: {FEEDBACK_PATH}")


def show_feedback(limit_days: int = 7):
    data = _load()
    # naive: print last N day keys
    days = sorted(data.keys(), reverse=True)[:limit_days]
    out = {d: data[d] for d in reversed(days)}
    print(json.dumps(out, indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print("Usage: varys-spider feedback [add|show] ...")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "add":
        # varys-spider feedback add 4 "comment ..."
        rating = None
        rest = sys.argv[2:]
        if rest and rest[0].isdigit():
            rating = int(rest[0])
            rest = rest[1:]
        comment = " ".join(rest).strip() or "(no comment)"
        add_feedback(rating=rating, comment=comment)
        return

    if cmd == "show":
        show_feedback()
        return

    print("Usage:")
    print("  varys-spider feedback add 4 \"Moltbook那条置信度应该更低\"")
    print("  varys-spider feedback show")
    sys.exit(1)


if __name__ == "__main__":
    main()
