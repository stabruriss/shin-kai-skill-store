"""Format output for text and TTS"""
from typing import List, Dict
from datetime import datetime
from datetime import timezone, timedelta
import re
import os
from scripts.translate import translate_to_chinese


def get_pacific_time() -> datetime:
    """Get current time in Pacific timezone"""
    pacific = timezone(timedelta(hours=-8))
    now_utc = datetime.now(timezone.utc)
    return now_utc.astimezone(pacific)


def format_text_digest(items: List[Dict], edition: str, config: Dict) -> str:
    """Format items into text digest with inline citations and auto-translation"""
    divider = "——————————————————"
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    lines = []
    
    # Header - use Pacific Time
    now_pt = get_pacific_time()
    lines.append(f"🕷️ Varys Spider 情报简报")
    lines.append(f"{now_pt.strftime('%Y年%m月%d日')} 太平洋时间 {now_pt.strftime('%H:%M')} {edition}")
    lines.append(f"共 {len(items)} 条信息\n")
    lines.append("=" * 40)
    lines.append("")
    
    # Items
    for i, item in enumerate(items):
        trust = item.get("trust_level", {})
        trust_emoji = trust.get("emoji", "💭")
        trust_name = trust.get("name", "个人观点")
        
        author = item.get("author", "Unknown")
        content = item.get("content", "")
        url = item.get("url", "")
        citations = item.get("citations", [])
        source = item.get("source", "unknown")
        is_chinese = is_content_chinese(content)
        is_japanese = is_content_japanese(content)
        
        # Determine emoji for item
        item_emoji = get_item_emoji(item, source)
        
        # Build item block
        lines.append("—-")
        lines.append("")
        lines.append(f"{item_emoji} {author}")
        lines.append("")
        lines.append(divider)
        lines.append(f"可信度：{trust_emoji} {trust_name}")
        lines.append(divider)
        
        # Content handling with auto-translation
        if source == "perplexity":
            # Perplexity returns Chinese summary - clean citation markers
            lines.append("[内容]")
            # Remove citation markers like [1], [2], [3]
            clean_content = re.sub(r'\[\d+\]', '', content)
            lines.append(clean_content.strip())
        else:
            # For Twitter/Bird and other sources
            max_chars = 500
            display_content = content[:max_chars] if len(content) > max_chars else content
            
            if is_chinese:
                lines.append(display_content)
            elif is_japanese:
                lines.append("[原文 - 日语]")
                lines.append(display_content)
                lines.append("")
                lines.append("[翻译]")
                if api_key:
                    print(f"   🌐 Translating Japanese item {i+1}/{len(items)}...")
                    translation = translate_to_chinese(display_content, api_key)
                    lines.append(translation)
                else:
                    lines.append("(原文为日语)")
            else:
                # English content - auto translate
                lines.append(display_content)
                lines.append("")
                lines.append("[翻译]")
                if api_key:
                    print(f"   🌐 Translating item {i+1}/{len(items)} from {author}...")
                    translation = translate_to_chinese(display_content, api_key)
                    lines.append(translation)
                else:
                    lines.append("(翻译服务暂不可用)")
        
        # Inline citations (optional, hide if too many)
        if source != "perplexity":
            lines.append("")
            if citations and len(citations) > 0:
                lines.append(f"来源: {citations[0]}")
            elif url:
                lines.append(f"来源: {url}")
        
        lines.append("")
        lines.append("————")
        lines.append("")
    
    return "\n".join(lines)


def format_tts_script(items: List[Dict], edition: str, config: Dict) -> str:
    """Format TTS script using mixed Perplexity + Twitter content with LLM summarization"""
    audio_config = config["output"]["audio"]
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    now_pt = get_pacific_time()
    intro = audio_config["intro_template"].format(
        date=now_pt.strftime('%Y年%m月%d日'),
        time=now_pt.strftime('%H:%M'),
        edition=edition
    )
    
    # Filter valid items
    valid_items = [item for item in items if is_valid_for_tts(item)]
    
    # Separate Perplexity and Twitter items
    perplexity_items = [item for item in valid_items if item.get("source") == "perplexity"]
    twitter_items = [item for item in valid_items if item.get("source") == "bird"]
    
    # Generate Chinese summary using LLM
    tts_content = generate_mixed_summary(perplexity_items, twitter_items, api_key)
    
    lines = [intro, ""]
    lines.append("今日要点：")
    lines.append("")
    lines.append(tts_content)
    lines.append("")
    lines.append(audio_config["outro_template"].format(next_edition="下次简报"))
    
    return "\n".join(lines)


def generate_mixed_summary(perplexity_items: List[Dict], twitter_items: List[Dict], api_key: str) -> str:
    """Use LLM to generate Chinese summary from mixed sources"""
    if not perplexity_items and not twitter_items:
        return "1。今日暂无重要更新。"
    
    # Build context from items
    context_parts = []
    
    if perplexity_items:
        context_parts.append("=== 新闻汇总 ===")
        for item in perplexity_items[:5]:
            headline = item.get("headline", "")
            content = item.get("content", "")[:300]
            context_parts.append(f"- {headline}: {content}")
    
    if twitter_items:
        context_parts.append("\n=== Twitter 观点 ===")
        for item in twitter_items[:5]:
            author = item.get("author", "")
            content = item.get("content", "")[:200]
            context_parts.append(f"- @{author}: {content}")
    
    context = "\n".join(context_parts)
    
    # If no API key, fallback to simple extraction
    if not api_key:
        return extract_simple_summary(perplexity_items, twitter_items)
    
    # Use LLM to generate Chinese summary
    prompt = f"""根据以下信息源，生成一份中文简报摘要，适合语音播报。

要求：
1. 用中文输出，自然流畅，适合朗读
2. 限制在 3-5 个要点，每个要点一句话
3. 优先 Perplexity 新闻，Twitter 作为观点补充
4. 不要包含英文原句（人名/公司名除外）
5. 格式：数字开头，如 "1。内容..."

信息源：
{context}

输出格式（纯中文）：
1。要点一...
2。要点二...
3。要点三..."""

    try:
        import json
        from urllib.request import Request, urlopen
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openclaw.ai",
            "X-Title": "Varys Spider TTS"
        }
        
        payload = json.dumps({
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 800
        }).encode('utf-8')
        
        req = Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers=headers,
            method='POST'
        )
        
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            summary = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Clean up the output
            summary = clean_tts_output(summary)
            if summary:
                return summary
    except Exception as e:
        print(f"   ⚠️ LLM summary failed: {e}")
    
    # Fallback
    return extract_simple_summary(perplexity_items, twitter_items)


def extract_simple_summary(perplexity_items: List[Dict], twitter_items: List[Dict]) -> str:
    """Fallback: extract simple summary without LLM"""
    lines = []
    
    # Use Perplexity headlines
    for i, item in enumerate(perplexity_items[:5], 1):
        headline = item.get("headline", "")
        if headline:
            lines.append(f"{i}。{headline}")
    
    # If no perplexity, use Twitter authors
    if not lines and twitter_items:
        authors = list(set([item.get("author", "") for item in twitter_items[:5]]))
        if authors:
            lines.append(f"1。Twitter 上 {', '.join(authors)} 等分享了最新动态。")
    
    if not lines:
        lines.append("1。今日暂无重要更新。")
    
    return "\n".join(lines[:5])


def clean_tts_output(text: str) -> str:
    """Clean LLM output for TTS"""
    if not text:
        return ""
    
    # Remove markdown
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'#+\s*', '', text)
    
    # Extract numbered lines
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if re.match(r'^\d+[\.。]\s*', line):
            # Clean the number format
            line = re.sub(r'^(\d+)[\.。]\s*', r'\1。', line)
            lines.append(line)
    
    return '\n'.join(lines) if lines else text


def is_valid_for_tts(item: Dict) -> bool:
    """Check if item content is valid for TTS (not error/disclaimer)"""
    content = item.get("content", "")
    if not content:
        return False
    
    # Skip error messages and disclaimers
    error_patterns = [
        "无法根据提供的搜索结果",
        "无法完成您的查询",
        "I cannot",
        "I apologize",
        "I'm unable to",
        "搜索失败",
        "抱歉",
        "没有找到",
    ]
    
    for pattern in error_patterns:
        if pattern in content[:200]:
            return False
    
    return True


def is_meaningful_sentence(sent: str) -> bool:
    """Check if sentence is meaningful for TTS"""
    if len(sent) < 15:
        return False
    if sent.startswith("http"):
        return False
    
    # Skip error-like content
    skip_prefixes = [
        "无法", "I cannot", "I'm unable", "抱歉", "Sorry",
        "请注意", "Note that", "免责声明", "Disclaimer"
    ]
    for prefix in skip_prefixes:
        if sent.startswith(prefix):
            return False
    
    return True


def clean_markdown(text: str) -> str:
    """Remove markdown syntax for TTS"""
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'\*', '', text)
    text = re.sub(r'__', '', text)
    text = re.sub(r'_', '', text)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[-*]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'https?://[^\s]+', '', text)
    text = re.sub(r'@[\w]+', '', text)
    text = re.sub(r'#[\w]+', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def get_item_emoji(item: Dict, source: str) -> str:
    """Get appropriate emoji for item"""
    priority = item.get("priority", "")
    
    if priority == "P1":
        return "🔥"
    elif priority == "P2":
        return "📰"
    elif source == "perplexity":
        return "🌐"
    elif source == "bird":
        return "🐦"
    else:
        return "📄"


def is_content_chinese(content: str) -> bool:
    """Detect if content is primarily Chinese"""
    if not content:
        return False
    chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
    return chinese_chars > len(content) * 0.1


def is_content_japanese(content: str) -> bool:
    """Detect if content is primarily Japanese"""
    if not content:
        return False
    japanese_chars = sum(1 for c in content if ('\u3040' <= c <= '\u309F') or ('\u30A0' <= c <= '\u30FF'))
    return japanese_chars > len(content) * 0.05
