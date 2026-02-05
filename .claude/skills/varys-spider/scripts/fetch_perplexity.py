"""Fetch data from Perplexity via OpenRouter with time-slot awareness and deduplication"""
import os
import json
import re
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from scripts.dedup import get_time_slot, load_reported_headlines, format_dedup_prompt, save_reported_headlines


def make_request(url: str, headers: Dict, data: bytes = None) -> Dict:
    """Make HTTP request using urllib"""
    req = Request(url, data=data, headers=headers, method='POST' if data else 'GET')
    try:
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {"error": e.code, "message": error_body[:500]}
    except Exception as e:
        return {"error": str(e)}


def fetch_perplexity_data(config: Dict, edition: str = "morning") -> List[Dict]:
    """Fetch search results from Perplexity using prompt-driven queries with deduplication"""
    pplx_config = config["sources"]["perplexity"]
    
    if not pplx_config.get("enabled", False):
        return []
    
    api_key = pplx_config.get("api_key", "")
    if not api_key:
        print("   ⚠️ OPENROUTER_API_KEY not set, skipping Perplexity source")
        return []
    
    base_url = pplx_config.get("base_url", "https://openrouter.ai/api/v1")
    model = pplx_config.get("model", "perplexity/sonar-pro")
    prompts = pplx_config.get("prompts", {})
    
    # Get time slot settings
    hours, time_desc = get_time_slot(edition)
    
    # Load already reported headlines for deduplication
    existing_headlines = load_reported_headlines()
    dedup_section = format_dedup_prompt(existing_headlines)
    
    all_items = []
    new_headlines = []
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "Varys Spider"
    }
    
    # Query each category
    for category, base_prompt in prompts.items():
        # Format prompt with time window and deduplication
        prompt = base_prompt.format(
            time_window=time_desc,
            dedup_section=dedup_section
        )
        
        print(f"   🔍 Perplexity {category}: {time_desc}...")
        
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }).encode('utf-8')
        
        data = make_request(f"{base_url}/chat/completions", headers, payload)
        
        if "error" not in data:
            try:
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                citations = data.get("citations", [])
                
                # Skip if no major updates
                if is_no_updates(content):
                    print(f"      ℹ️ No major updates for {category}")
                    continue
                
                items, headlines = parse_structured_response(content, citations, category)
                all_items.extend(items)
                new_headlines.extend(headlines)
                print(f"      Found {len(items)} items with {len(citations)} citations")
            except Exception as e:
                print(f"      Parse error: {e}")
        else:
            print(f"      Error: {data.get('message', data.get('error'))}")
    
    # Save new headlines for future deduplication
    if new_headlines:
        save_reported_headlines(new_headlines)
    
    return all_items


def is_no_updates(content: str) -> bool:
    """Check if content indicates no major updates"""
    no_update_phrases = [
        "no major updates",
        "no significant news",
        "no new developments",
        "暂无不重要更新",
        "暂无重要更新",
        "没有重大更新"
    ]
    content_lower = content.lower()
    return any(phrase in content_lower for phrase in no_update_phrases)


def parse_structured_response(content: str, citations: List[str], category: str) -> tuple:
    """Parse structured response into items and extract headlines"""
    items = []
    headlines = []
    
    if not content.strip():
        return items, headlines
    
    # Extract numbered items (1. **Headline**)
    pattern = r'\d+\.\s*\*\*([^*]+)\*\*'
    matches = list(re.finditer(pattern, content))
    
    for i, match in enumerate(matches):
        headline = match.group(1).strip()
        headlines.append(headline)
        
        # Extract content for this item (from this match to next)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        item_content = content[start:end].strip()
        
        item = {
            "id": f"pplx_{category}_{hash(headline) % 10000}",
            "source": "perplexity",
            "category": category,
            "author": category.replace("_", " ").title(),
            "headline": headline,
            "content": f"**{headline}**\n{item_content}",
            "url": citations[0] if citations else "",
            "citations": citations[:3],  # Limit citations
            "timestamp": datetime.now().isoformat(),
            "is_chinese": False  # Perplexity returns English
        }
        items.append(item)
    
    return items, headlines
