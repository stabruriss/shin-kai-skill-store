#!/usr/bin/env python3
"""collect.py - Multi-source collection for Varys Spider.

Each collected item is a dict with (at least):
- kind: rss|hn|github|techmeme|twitter
- source: human-readable source
- title: short headline or tweet first line
- url: optional
- tier_hint: citadel|little_birds|tavern_whispers

Where available we also include:
- text: longer body (RSS description, tweet full text)

"""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def http_get(url: str, timeout=15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "VarysSpider/0.4"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_rss(xml_text: str, source_name: str, max_items=10):
    items = []
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return items

    # RSS2: channel/item
    for it in root.findall(".//channel/item")[:max_items]:
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        desc = _strip_html(it.findtext("description") or "")
        if title:
            items.append({
                "source": source_name,
                "tier_hint": "citadel",
                "kind": "rss",
                "title": title,
                "url": link,
                "published": pub,
                "text": desc,
            })

    # Atom: entry
    if not items:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for e in root.findall(".//atom:entry", ns)[:max_items]:
            title = (e.findtext("atom:title", default="", namespaces=ns) or "").strip()
            link_el = e.find("atom:link", ns)
            link = link_el.get("href") if link_el is not None else ""
            updated = (e.findtext("atom:updated", default="", namespaces=ns) or "").strip()
            summ = _strip_html(e.findtext("atom:summary", default="", namespaces=ns) or "")
            if title:
                items.append({
                    "source": source_name,
                    "tier_hint": "citadel",
                    "kind": "rss",
                    "title": title,
                    "url": link,
                    "published": updated,
                    "text": summ,
                })

    return items


def collect_rss(cfg: dict):
    out = []
    feeds = cfg.get("feeds", [])
    for f in feeds:
        name = f.get("name", "RSS")
        url = f.get("url")
        if not url:
            continue
        try:
            xml_text = http_get(url)
            out.extend(parse_rss(xml_text, name, max_items=10))
        except Exception:
            continue
    return out


def collect_hackernews(cfg: dict):
    out = []
    min_score = int(cfg.get("min_score", 100))
    try:
        ids = json.loads(http_get("https://hacker-news.firebaseio.com/v0/topstories.json"))
    except Exception:
        return out

    for story_id in ids[:60]:
        try:
            item = json.loads(http_get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"))
        except Exception:
            continue
        if not item or item.get("type") != "story":
            continue
        if item.get("score", 0) < min_score:
            continue
        url = item.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
        out.append({
            "source": "Hacker News",
            "tier_hint": "little_birds",
            "kind": "hn",
            "title": item.get("title"),
            "url": url,
            "published": datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc).isoformat(),
            "score": item.get("score", 0),
            "text": "",  # could be filled by later fetch/summarize step
        })
        if len(out) >= 20:
            break

    return out


def collect_github(cfg: dict):
    out = []
    since = cfg.get("since", "daily")
    url = f"https://github.com/trending?since={since}"
    try:
        html = http_get(url)
    except Exception:
        return out

    repos = []
    for m in re.finditer(r'href="/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"', html):
        repos.append(m.group(1))

    seen = set()
    for r in repos:
        if r in seen:
            continue
        seen.add(r)
        out.append({
            "source": "GitHub Trending",
            "tier_hint": "little_birds",
            "kind": "github",
            "title": r,
            "url": f"https://github.com/{r}",
            "text": "",
        })
        if len(out) >= 20:
            break

    return out


def collect_techmeme(cfg: dict):
    out = []
    url = cfg.get("url", "https://techmeme.com")
    try:
        html = http_get(url)
    except Exception:
        return out

    links = re.findall(r'href="(https?://[^\"]+)"', html)
    seen = set()
    allow = ["reuters.com", "wsj.com", "nytimes.com", "theverge.com", "techcrunch.com", "arstechnica.com", "bbc.co.uk", "bbc.com", "apnews.com", "ft.com", "economist.com"]
    for u in links:
        if "techmeme.com" in u:
            continue
        if u in seen:
            continue
        seen.add(u)
        if not any(d in u for d in allow):
            continue
        out.append({
            "source": "Techmeme",
            "tier_hint": "citadel",
            "kind": "techmeme",
            "title": u,
            "url": u,
            "text": "",
        })
        if len(out) >= 20:
            break

    return out


def _bird_available() -> bool:
    return subprocess.run(["which", "bird"], capture_output=True).returncode == 0


def collect_twitter(cfg: dict):
    """Collect tweets.

    focus_mode:
      - "prefer": prioritize focus_accounts but allow others if insufficient
      - "only": only include focus_accounts
    """

    out = []
    if not _bird_available():
        return out

    max_items = int(cfg.get("max_items", 80))
    focus = [a.lower().lstrip("@") for a in (cfg.get("focus_accounts") or [])]
    focus_mode = (cfg.get("focus_mode") or "prefer").lower()

    auth_token = os.environ.get("AUTH_TOKEN")
    ct0 = os.environ.get("CT0")

    if not (auth_token and ct0):
        try:
            from pathlib import Path
            p = Path.home() / ".openclaw" / "varys-spider" / "bird-secrets.json"
            if p.exists():
                s = json.loads(p.read_text("utf-8"))
                auth_token = auth_token or s.get("auth_token")
                ct0 = ct0 or s.get("ct0")
        except Exception:
            pass

    cmd = ["bird"]
    if auth_token and ct0:
        cmd += ["--auth-token", auth_token, "--ct0", ct0]
    cmd += ["home", "--following", "-n", str(max_items)]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        txt = res.stdout
    except Exception:
        return out

    blocks = [b.strip() for b in txt.split("──────────────────────────────────────────────────") if b.strip()]
    for b in blocks:
        lines = [l for l in b.splitlines() if l.strip()]
        if not lines:
            continue
        first = lines[0]
        m = re.match(r"^(@[^\s]+)", first)
        handle = m.group(1) if m else "@unknown"
        handle_norm = handle.lower().lstrip("@")

        is_focus = (not focus) or (handle_norm in focus)
        if focus and (not is_focus) and focus_mode == "only":
            continue

        url = ""
        for l in lines:
            if l.startswith("🔗 ") and "https://x.com/" in l:
                url = l.replace("🔗 ", "").strip()
                break

        content_lines = []
        for l in lines[1:]:
            if l.startswith("📅") or l.startswith("🔗"):
                break
            if l.startswith("🖼️") or l.startswith("🎬") or l.startswith("┌─") or l.startswith("└─") or l.startswith("│"):
                continue
            content_lines.append(l)
        content = "\n".join(content_lines).strip()

        # Clean up duplicate t.co links in content (keep first occurrence only)
        seen_links = set()
        cleaned_lines = []
        for ln in content.splitlines():
            # Remove duplicate t.co links
            if "https://t.co/" in ln:
                # Extract all t.co links
                import re as _re
                links = _re.findall(r'https://t\.co/\w+', ln)
                new_ln = ln
                for link in links:
                    if link in seen_links:
                        new_ln = new_ln.replace(link, "")
                    else:
                        seen_links.add(link)
                new_ln = _re.sub(r'\s+', ' ', new_ln).strip()
                if new_ln:
                    cleaned_lines.append(new_ln)
            else:
                cleaned_lines.append(ln)
        content = "\n".join(cleaned_lines).strip()

        # Use first line as title (not truncated), or handle if very long
        first_line = content.splitlines()[0] if content else first
        if len(first_line) > 200:
            first_line = first_line[:197] + "..."

        out.append({
            "source": handle,
            "tier_hint": "tavern_whispers" if not is_focus else "little_birds",
            "kind": "twitter",
            "title": first_line,
            "url": url,
            "text": content,
            "focus": bool(is_focus),
        })

    return out
