"""Signal scoring and quality gates"""
from typing import List, Dict
from collections import Counter


def score_signal(items: List[Dict], config: Dict) -> List[Dict]:
    """Apply signal scoring and quality gates"""
    
    # Separate Perplexity items (keep them all, they're high quality)
    perplexity_items = [i for i in items if i.get("source") == "perplexity"]
    other_items = [i for i in items if i.get("source") != "perplexity"]
    
    # Add signal scores to all items
    for item in items:
        item["signal_score"] = calculate_signal_score(item)
        item["signal_tier"] = get_signal_tier(item)
    
    # Filter other items by threshold (not Perplexity)
    threshold = config["quality"]["signal_threshold"]
    filtered_other = [i for i in other_items if i["signal_score"] >= threshold]
    
    # Combine: Perplexity items + filtered other items
    items = perplexity_items + filtered_other
    
    # Sort by score
    items.sort(key=lambda x: x["signal_score"], reverse=True)
    
    # Apply diversity gate
    items = apply_diversity_gate(items, config)
    
    # Apply signal gate (must have at least 1 P2 or P3)
    items = apply_signal_gate(items, config)
    
    return items


def calculate_signal_score(item: Dict) -> int:
    """Calculate signal score for an item"""
    score = 0
    
    # Base score from trust level
    trust_score = item.get("trust_level", {}).get("score", 1)
    score += trust_score * 2
    
    # Priority bonus
    priority = item.get("priority", "P3")
    if priority == "P1":
        score += 10
    elif priority == "P2":
        score += 5
    else:
        score += 2
    
    # Content quality signals
    content = item.get("content", "")
    if len(content) > 100:
        score += 2
    if "http" in content:  # Has link
        score += 1
    
    return score


def get_signal_tier(item: Dict) -> str:
    """Get signal tier (P1/P2/P3/none)"""
    score = item.get("signal_score", 0)
    if score >= 15:
        return "P3"
    elif score >= 12:
        return "P2"
    elif score >= 10:
        return "P1"
    else:
        return "none"


def apply_diversity_gate(items: List[Dict], config: Dict) -> List[Dict]:
    """Ensure diversity: max per author, min signal diversity"""
    max_per_author = config["quality"]["max_per_author"]
    min_diversity = config["quality"]["min_diversity"]
    
    # Limit per author - max 2 per author as requested
    author_counts = Counter()
    filtered = []
    
    for item in items:
        author = item.get("author", "unknown")
        source = item.get("source", "unknown")
        
        # For Perplexity, allow more items since it's curated content
        limit = max_per_author if source != "perplexity" else 5
        
        if author_counts[author] < limit:
            filtered.append(item)
            author_counts[author] += 1
    
    # Check signal diversity
    signal_tiers = set(i["signal_tier"] for i in filtered if i["signal_tier"] != "none")
    if len(signal_tiers) < min_diversity:
        # Not enough diversity, but continue anyway with warning
        print(f"   ⚠️ Signal diversity low: {len(signal_tiers)} tiers (min {min_diversity})")
    
    return filtered[:30]  # Max 30 items


def apply_signal_gate(items: List[Dict], config: Dict) -> List[Dict]:
    """Must have at least 1 P2 or P3 item"""
    min_p2_p3 = config["quality"]["min_p2_p3_count"]
    
    p2_p3_count = sum(1 for i in items if i["signal_tier"] in ["P2", "P3"])
    
    if p2_p3_count < min_p2_p3:
        print(f"   ⚠️ Signal gate warning: only {p2_p3_count} P2/P3 items (min {min_p2_p3})")
        # Continue but mark as fallback
    
    return items
