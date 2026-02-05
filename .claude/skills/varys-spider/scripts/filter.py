"""Filter and deduplicate items using LLM-based quality assessment"""
import os
from typing import List, Dict
from scripts.llm_judge import assess_content_validity


def filter_items(items: List[Dict], config: Dict) -> List[Dict]:
    """Apply LLM-based filtering to remove low-quality content"""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    filtered = []
    seen_content = set()
    
    for item in items:
        content = item.get("content", "")
        source = item.get("source", "unknown")
        author = item.get("author", "Unknown")
        
        # Skip empty
        if not content or len(content) < 20:
            continue
        
        # Simple deduplication (content hash)
        content_hash = hash(content.lower().strip()[:100])
        if content_hash in seen_content:
            continue
        seen_content.add(content_hash)
        
        # LLM-based quality assessment
        if api_key:
            assessment = assess_content_validity(content, source, author, api_key)
            if not assessment.get("valid", True):
                print(f"      🚫 Filtered ({author}): {assessment.get('reason', 'Low quality')[:50]}")
                continue
            # Store assessment results for later use
            item['_quality_assessment'] = assessment
        
        filtered.append(item)
    
    print(f"   After LLM filtering: {len(filtered)} items")
    return filtered
