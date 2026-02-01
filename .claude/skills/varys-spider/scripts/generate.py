#!/usr/bin/env python3
"""generate.py - Generate briefing using config.json.

Goals (per user feedback):
- Chinese briefing by default
- Include a legend explaining seals
- Prefer not to require clicking links: include ~200 Chinese chars summary per item
  - For tweets: quote full tweet text
  - For RSS: use RSS description/summary when available
  - For others: best-effort short "what it is" line (can be improved later)

NOTE: Deep summarization/translation is better done by an LLM agent layer.
This script provides a useful offline baseline.

"""

from __future__ import annotations

from datetime import datetime

from config import load_config
from collect import (
    collect_rss,
    collect_hackernews,
    collect_github,
    collect_techmeme,
    collect_twitter,
)
from verify import cluster, filter_by_topics


LEGEND_ZH = (
    "图例（置信度/来源等级）：\n"
    "- 🌍 Spider's Web：多家权威来源交叉验证\n"
    "- 📻 The Citadel：权威媒体/机构来源\n"
    "- 📣 Little Birds：社区/多源汇总\n"
    "- 🍻 Tavern Whispers：单一社交信源（需谨慎）\n"
    "- 🧻 The Dungeons：未经验证的传闻\n"
)


def _classify(c: dict) -> str:
    """Return one of: finance|policy|tech|fun|other"""
    text = ((c.get("title") or "") + " " + (c.get("url") or "") + " " + " ".join(c.get("sources") or [])).lower()

    finance_kw = [
        "market", "stocks", "bond", "yields", "yield", "rates", "fed", "inflation", "cpi", "jobs report", "earnings",
        "selloff", "rally", "crash", "surge", "plunge", "nasdaq", "s&p", "dow",
        "美元", "美债", "利率", "降息", "加息", "通胀", "非农", "财报", "暴涨", "暴跌",
    ]
    policy_kw = [
        "immigration", "border", "election", "primary", "campaign", "white house", "congress", "sanctions",
        "war", "conflict", "strike", "gaza", "ukraine", "russia", "israel", "iran", "china", "taiwan",
        "移民", "边境", "选举", "国会", "制裁", "战争", "冲突", "中美", "地缘", "台湾", "乌克兰", "以色列",
    ]
    tech_kw = [
        "ai", "llm", "openai", "anthropic", "google", "deepmind", "microsoft", "meta", "nvidia", "amd",
        "acquisition", "merger", "funding", "investment", "layoff", "ipo",
        "paper", "arxiv", "benchmark", "agent",
        "人工智能", "大模型", "并购", "收购", "融资", "投资", "裁员", "论文", "模型", "agent",
    ]
    fun_kw = [
        "meme", "viral", "trend", "phenomenon",
        "梗", "现象", "爆火", "热议", "出圈",
    ]

    if any(k in text for k in finance_kw):
        return "finance"
    if any(k in text for k in policy_kw):
        return "policy"
    if any(k in text for k in tech_kw):
        return "tech"
    if any(k in text for k in fun_kw):
        return "fun"
    return "other"


def _render_section(title: str, clusters: list[dict], lang: str) -> list[str]:
    lines = [title]
    if not clusters:
        lines.append("- （没有）" if lang == "zh" else "- (none)")
        lines.append("")
        return lines

    for c in clusters:
        seal, label, conf = c["seal"]
        lines.append(f"{seal} [{label}] ({int(conf*100)}%)")

        # best-effort body
        kind = c.get("kind")
        # For non-twitter, show title; for twitter, skip artificial title line
        if kind != "twitter" and c.get("title"):
            lines.append(f"- 标题：{c['title']}")

        if kind == "twitter" and c.get("text"):
            # quote tweet - show full content with soft limit
            text = c["text"]
            lines.append("- 推文：")
            # If tweet is extremely long (>800 chars), show first 600 + ellipsis note
            if len(text) > 800:
                preview = text[:600]
                for ln in preview.splitlines():
                    lines.append(f"  {ln}")
                lines.append("  ...（推文较长，已截断，建议点击链接查看完整内容）")
            else:
                for ln in text.splitlines():
                    lines.append(f"  {ln}")
        elif c.get("text"):
            # RSS description or similar
            snippet = c["text"].strip()
            snippet = snippet[:220]
            if snippet:
                lines.append(f"- 摘要：{snippet}")
        else:
            lines.append("- 摘要：（暂无，建议点开链接查看详情）")

        if c.get("sources"):
            lines.append(f"- 来源：{', '.join(c['sources'])}")
        if c.get("url"):
            lines.append(f"- 链接：{c['url']}")
        lines.append("")

    return lines


def _render(clusters: list[dict], cfg: dict) -> str:
    lang = cfg.get("output", {}).get("language", "zh")
    tz = cfg.get("output", {}).get("timezone", "")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    header = f"🕷️ Varys Spider 情报简报\n时间: {now} ({tz})\n"

    titles = {
        "finance": "金融市场重大变化",
        "policy": "政治政策热点事件",
        "tech": "科技圈新闻",
        "fun": "有趣的事情",
        "other": "其他",
    }

    buckets = {k: [] for k in titles.keys()}
    for c in clusters:
        buckets[_classify(c)].append(c)

    lines = [header, "", LEGEND_ZH, ""]
    lines += _render_section(f"## {titles['finance']}", buckets["finance"], lang)
    lines += _render_section(f"## {titles['policy']}", buckets["policy"], lang)
    lines += _render_section(f"## {titles['tech']}", buckets["tech"], lang)
    lines += _render_section(f"## {titles['fun']}", buckets["fun"], lang)
    lines += _render_section(f"## {titles['other']}", buckets["other"], lang)

    return "\n".join(lines).strip() + "\n"


def _quota_select(clusters: list[dict], cfg: dict) -> list[dict]:
    max_items = int(cfg.get("output", {}).get("max_items", 20))
    ordering = cfg.get("output", {}).get("ordering", "quota_then_confidence")
    mix = cfg.get("mix", {})

    if ordering == "confidence_only":
        return clusters[:max_items]

    quotas = {k: int(v) for k, v in mix.items() if isinstance(v, (int, float))}

    picked = []
    used = set()

    def take(kind: str, n: int):
        if n <= 0:
            return
        cnt = 0
        for i, c in enumerate(clusters):
            if len(picked) >= max_items:
                return
            if i in used:
                continue
            if c.get("kind") == kind:
                picked.append(c)
                used.add(i)
                cnt += 1
                if cnt >= n:
                    return

    # Prefer Twitter as primary source, then fill with others as supplement.
    take("twitter", quotas.get("twitter", 0))
    take("rss", quotas.get("rss", 0))
    take("hn", quotas.get("hackernews", 0))
    take("techmeme", quotas.get("techmeme", 0))
    take("github", quotas.get("github", 0))

    for i, c in enumerate(clusters):
        if len(picked) >= max_items:
            break
        if i in used:
            continue
        picked.append(c)
        used.add(i)

    return picked


def main():
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

    # carry text forward into clusters (representative item text)
    clusters = cluster(items)
    # attach text by matching title/url where possible (simple)
    by_key = {}
    for it in items:
        key = (it.get("kind"), it.get("title"), it.get("url"))
        if key not in by_key:
            by_key[key] = it
    for c in clusters:
        it = by_key.get((c.get("kind"), c.get("title"), c.get("url")))
        if it and it.get("text"):
            c["text"] = it.get("text")

    selected = _quota_select(clusters, cfg)

    print(_render(selected, cfg))


if __name__ == "__main__":
    main()
