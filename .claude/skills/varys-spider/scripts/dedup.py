"""Deduplication storage for daily headlines"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Set


def get_dedup_file_path() -> Path:
    """Get today's deduplication file path"""
    today = datetime.now().strftime("%Y-%m-%d")
    cache_dir = Path(__file__).parent.parent / "cache" / "dedup"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"reported_headlines_{today}.json"


def load_reported_headlines() -> Set[str]:
    """Load today's already reported headlines"""
    dedup_file = get_dedup_file_path()
    if dedup_file.exists():
        try:
            with open(dedup_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("headlines", []))
        except Exception:
            pass
    return set()


def save_reported_headlines(headlines: List[str]):
    """Save headlines to today's deduplication file"""
    dedup_file = get_dedup_file_path()
    existing = load_reported_headlines()
    existing.update(headlines)
    
    with open(dedup_file, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "headlines": list(existing)
        }, f, ensure_ascii=False, indent=2)


def get_time_slot(edition: str) -> tuple:
    """Get time window hours and description for edition"""
    slots = {
        "morning": (12, "overnight developments (past 12 hours)"),
        "afternoon": (6, "morning developments (past 6 hours)"),
        "evening": (6, "afternoon developments (past 6 hours)"),
        "night": (24, "daily summary of most significant stories")
    }
    return slots.get(edition, (6, "recent developments"))


def format_dedup_prompt(existing_headlines: Set[str]) -> str:
    """Format already reported headlines for prompt injection"""
    if not existing_headlines:
        return ""
    
    headlines_text = "\n".join([f"- {h}" for h in list(existing_headlines)[:20]])
    return f"""
Already reported today (AVOID these topics, focus on NEW developments):
{headlines_text}

Remember: Only report NEW stories not listed above. If no new significant stories, return "No major updates".
"""
