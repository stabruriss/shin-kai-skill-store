"""Translate content using OpenRouter"""
import os
import json
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def translate_to_chinese(text: str, api_key: Optional[str] = None) -> str:
    """Translate English text to Chinese using OpenRouter"""
    if not text or len(text.strip()) < 10:
        return text
    
    # Check if already mostly Chinese
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    if chinese_chars > len(text) * 0.3:
        return text  # Already Chinese
    
    if not api_key:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    if not api_key:
        return "[翻译失败：未设置 API Key]"
    
    try:
        prompt = f"请将以下英文翻译成自然流畅的中文：\n\n{text[:1000]}\n\n翻译："
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openclaw.ai",
            "X-Title": "Varys Spider Translation"
        }
        
        payload = json.dumps({
            "model": "openai/gpt-4o-mini",  # Fast and cheap for translation
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }).encode('utf-8')
        
        req = Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers=headers,
            method='POST'
        )
        
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            translation = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return translation.strip() if translation else "[翻译失败]"
            
    except Exception as e:
        print(f"      ⚠️ Translation error: {e}")
        return "[翻译失败，请稍后再试]"
