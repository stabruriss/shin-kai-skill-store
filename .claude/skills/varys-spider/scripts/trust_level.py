"""Classify trust level for items using LLM-based assessment"""
import os
from typing import Dict
from scripts.llm_judge import call_llm_judge


def classify_trust_level(item: Dict, config: Dict) -> Dict:
    """Classify item into 5-tier trust level using LLM assessment"""
    trust_config = config["trust_levels"]
    source = item.get("source", "")
    author = item.get("author", "")
    content = item.get("content", "")[:500]
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    # If we already have LLM assessment from filtering, use it
    if "_quality_assessment" in item and api_key:
        assessment = item.pop("_quality_assessment")
        trust_level = assessment.get("trust_level", "community")
        return trust_config.get(trust_level, trust_config["community"])
    
    # Fallback to LLM classification if no prior assessment
    if api_key:
        prompt = f"""评估以下信息的可信度级别：

来源: {source}
作者: {author}
内容片段:
{content}

可信度级别定义：
- authoritative(🏛️): 权威媒体/官方来源（BBC、Reuters、WSJ等）
- professional(📊): 专业分析师/行业专家
- community(🔥): 社区讨论/热议话题
- personal(💭): 个人观点/社交媒体
- rumor(🍺): 未经证实/传闻

请只输出一个级别词（英文小写），例如: community"""

        result = call_llm_judge(prompt, api_key)
        level = result.get("trust_level", "community")
        return trust_config.get(level, trust_config["community"])
    
    # Fallback to simple source-based rules if no API
    if source == "perplexity":
        return trust_config["professional"]  # Perplexity is curated
    
    # Simple fallback for Bird sources
    authoritative_accounts = [
        "BBCWorld", "BBCBreaking", "Reuters", "WSJ", "nytimes", "TheEconomist"
    ]
    professional_accounts = [
        "CookPolitical", "FiveThirtyEight", "DecisionDeskHQ", 
        "emollick", "gregisenberg"
    ]
    
    if author in authoritative_accounts:
        return trust_config["authoritative"]
    elif author in professional_accounts:
        return trust_config["professional"]
    else:
        return trust_config["community"]
