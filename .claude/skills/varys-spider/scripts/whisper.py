#!/usr/bin/env python3
"""whisper.py - Record natural-language feedback.

We intentionally don't auto-apply numeric confidence demotions.
We store the feedback durably (feedback.json) and optionally apply small,
explicit config toggles when user asks (e.g. enable/disable twitter).

"""

from __future__ import annotations

import re
import sys

from config import load_config, save_config
from feedback import add_feedback


def main():
    if len(sys.argv) < 2:
        print('Usage: varys-spider whisper "feedback"')
        sys.exit(1)

    text = " ".join(sys.argv[1:]).strip()
    low = text.lower()

    # Always record feedback
    rating = None
    m = re.match(r"^\s*(\d)\s+(.+)$", text)
    comment = text
    if m:
        rating = int(m.group(1))
        comment = m.group(2)

    add_feedback(rating=rating, comment=comment)

    # Optional explicit config toggles (only when user asks)
    cfg = load_config()
    changed = []

    if "disable twitter" in low or "关推特" in low or "关闭推特" in low:
        cfg["sources"]["twitter"]["enabled"] = False
        changed.append("sources.twitter.enabled=false")

    if "enable twitter" in low or "开推特" in low or "启用推特" in low:
        cfg["sources"]["twitter"]["enabled"] = True
        changed.append("sources.twitter.enabled=true")

    if "中文" in low:
        cfg["output"]["language"] = "zh"
        changed.append("output.language=zh")

    if "英文" in low or "english" in low:
        cfg["output"]["language"] = "en"
        changed.append("output.language=en")

    if changed:
        save_config(cfg)
        print("🕷️ Recorded feedback and updated config:\n- " + "\n- ".join(changed))
    else:
        print("🕷️ Recorded feedback.")


if __name__ == "__main__":
    main()
