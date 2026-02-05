"""LLM-based content quality assessment via OpenRouter"""
import json
from typing import Dict, List
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def call_llm_judge(prompt: str, api_key: str, model: str = "openai/gpt-4o-mini") -> Dict:
    """Call LLM to judge content quality"""
    if not api_key:
        return {"error": "No API key", "valid": True}  # Fail open
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "Varys Spider QA"
    }
    
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 500
    }).encode('utf-8')
    
    try:
        req = Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers=headers,
            method='POST'
        )
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return parse_llm_response(content)
    except Exception as e:
        return {"error": str(e), "valid": True}  # Fail open


def parse_llm_response(content: str) -> Dict:
    """Parse structured response from LLM"""
    result = {"valid": True, "reason": "", "trust_level": "community", "score": 3}
    
    # Look for structured output
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('VALID:') or line.startswith('有效:'):
            val = line.split(':', 1)[1].strip().lower()
            result['valid'] = val in ['yes', 'true', '是', '有效', 'true']
        elif line.startswith('REASON:') or line.startswith('原因:'):
            result['reason'] = line.split(':', 1)[1].strip()
        elif line.startswith('TRUST:') or line.startswith('可信度:'):
            level = line.split(':', 1)[1].strip().lower()
            result['trust_level'] = normalize_trust_level(level)
        elif line.startswith('SCORE:') or line.startswith('评分:'):
            try:
                result['score'] = int(line.split(':', 1)[1].strip())
            except:
                pass
    
    return result


def normalize_trust_level(level: str) -> str:
    """Normalize trust level to standard values"""
    level = level.lower()
    if any(k in level for k in ['authoritative', '权威', '官方', '事实']):
        return "authoritative"
    elif any(k in level for k in ['professional', '专业', '分析', '评论']):
        return "professional"
    elif any(k in level for k in ['community', '社区', '热议', '讨论']):
        return "community"
    elif any(k in level for k in ['personal', '个人', '观点', '看法']):
        return "personal"
    elif any(k in level for k in ['rumor', '传闻', '谣言', '小道']):
        return "rumor"
    return "community"


def assess_content_validity(content: str, source: str, author: str, api_key: str) -> Dict:
    """Use LLM to assess if content is valid and valuable"""
    prompt = f"""你是一个内容质量评估专家。请评估以下信息是否有效且值得收录到情报简报中。

内容来源: {source}
作者: {author}
内容:
---
{content[:800]}
---

请评估:
1. 这是否是一个有效的信息（不是错误消息、免责声明、系统提示等）
2. 这条信息是否有情报价值（不是垃圾信息、广告、无意义的转发等）

请按以下格式输出:
VALID: [yes/no]  # 内容是否有效且有价值
REASON: [简要说明原因]
TRUST: [authoritative/professional/community/personal/rumor]  # 判断可信度级别
SCORE: [1-5]  # 信息质量评分

注意：如果内容是"无法完成查询"、"搜索失败"、"I cannot"等错误提示，请标记为 INVALID。"""

    return call_llm_judge(prompt, api_key)
