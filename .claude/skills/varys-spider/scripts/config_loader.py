"""Configuration loader - simplified version without PyYAML dependency"""
import os
import re
from pathlib import Path


def load_config():
    """Load configuration from YAML file with environment variable substitution"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Simple environment variable substitution
    def env_replacer(match):
        var_name = match.group(1)
        return os.environ.get(var_name, "")
    
    content = re.sub(r'\$\{([^}]+)\}', env_replacer, content)
    
    # Parse simple YAML structure manually
    config = parse_simple_yaml(content)
    return config


def parse_simple_yaml(content):
    """Parse a simplified YAML structure"""
    config = {}
    current_dict = config
    dict_stack = []
    current_key = None
    
    for line in content.split('\n'):
        # Skip comments and empty lines
        line = line.split('#')[0].rstrip()
        if not line.strip():
            continue
        
        # Count indentation
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        
        # Handle different indentation levels
        while len(dict_stack) * 2 > indent and dict_stack:
            current_dict = dict_stack.pop()
        
        if ':' in stripped:
            key, val = stripped.split(':', 1)
            key = key.strip()
            val = val.strip()
            
            if val == '':
                # New nested dict
                current_dict[key] = {}
                dict_stack.append(current_dict)
                current_dict = current_dict[key]
            elif val.startswith('[') and val.endswith(']'):
                # List
                current_dict[key] = [v.strip().strip('"\'') for v in val[1:-1].split(',')]
            elif val in ['true', 'True']:
                current_dict[key] = True
            elif val in ['false', 'False']:
                current_dict[key] = False
            elif val.isdigit():
                current_dict[key] = int(val)
            else:
                current_dict[key] = val.strip('"\'')
    
    # Hardcode some structures that are hard to parse
    config = build_default_config()
    return config


def build_default_config():
    """Build default configuration"""
    return {
        "sources": {
            "bird": {
                "enabled": True,
                "bearer_token": os.environ.get("BIRD_BEARER_TOKEN", ""),
                "focus_accounts": [
                    # AI/Tech Core (from sodawhite_dev list)
                    "karpathy", "sama", "ylecun", "andrewyng", "fchollet",
                    "drjimfan", "emollick", "hwchase17", "jerryjliu0", "simonw",
                    "hamelhusain", "swyx", "mckaywrigley", "amasad", "rauchg",
                    "_akhaliq", "geoffreylitt", "goodside", "alexalbert__",
                    "mattshumer_", "godofprompt", "rowancheung", "linusekenstam",
                    "heybarsee", "itspaulai", "bentossell", "aaditsh", "petergyang",
                    # Original AI/Tech
                    "mranti", "wuyuesanren", "op7418", "dair_ai", "yetone",
                    "steipete", "bcherny", "gregisenberg",
                    # Finance/Trading
                    "WallStTV", "yriica", "fxtrader", "rryssf_",
                    # Politics/Polling
                    "CookPolitical", "FiveThirtyEight", "DecisionDeskHQ",
                    "Redistrict", "gelliottmorris",
                    # Mainstream Media
                    "BBCWorld", "BBCBreaking", "Reuters", "WSJ",
                    "nytimes", "TheEconomist",
                    # Chinese Community
                    "renfanzi", "dotey", "lifesinger", "vista8",
                    "fanshimin", "superzen", "Alex8282019",
                    "lxfater", "wshuyi", "oran_ge", "imxiaohu"
                ],
                "max_items": 100,
                "max_per_author": 2,
                "include_replies": False,
                "include_retweets": True,
                "time_window_hours": 6
            },
            "perplexity": {
                "enabled": True,
                "api_key": os.environ.get("OPENROUTER_API_KEY", ""),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "perplexity/sonar-pro",
                "max_items_per_query": 10,
                "prompts": {
                    "P1_AI": """# Daily Briefing — AI & Tech
Search: Hacker News, Reddit (r/MachineLearning, r/LocalLLaMA, r/OpenAI), ArsTechnica, The Verge, Reuters Tech, TechCrunch
Topics: model releases, research papers, open-source projects, AI policy/regulation, major product launches, industry drama
Time window: {time_window}
Rules:
1. English sources ONLY
2. If no significant news, return "No major updates" — never fabricate
3. Prioritize breaking/developing stories over analysis pieces
4. Max 3-5 items
{dedup_section}
Output format:
1. **[Topic headline]**
   - What: [1-2 sentence summary]
   - Why it matters: [brief impact]
   - Source: [Publication](URL)""",
                    "P2_Immigration": """# Daily Briefing — US Immigration
Search: USCIS.gov, Reuters, AP, Law360, Reddit r/immigration, r/h1b
Topics: H1B/EB green card policy changes, visa bulletin updates, USCIS processing news, court rulings, fee changes
Time window: {time_window}
Rules:
1. English sources ONLY
2. If no significant news, return "No major updates" — never fabricate
3. Focus on official policy changes and major updates
4. Max 2-3 items
{dedup_section}
Output format:
1. **[Topic headline]**
   - What: [1-2 sentence summary]
   - Why it matters: [brief impact]
   - Source: [Publication](URL)""",
                    "P3_Politics": """# Daily Briefing — Politics & Geopolitics
Search: Reuters, AP, BBC, WSJ, The Economist
Topics: US domestic politics, US-China relations, major international conflicts, elections, significant legislation
Time window: {time_window}
Rules:
1. English sources ONLY
2. If no significant news, return "No major updates" — never fabricate
3. Prioritize breaking/developing stories
4. Max 3-5 items
{dedup_section}
Output format:
1. **[Topic headline]**
   - What: [1-2 sentence summary]
   - Why it matters: [brief impact]
   - Source: [Publication](URL)""",
                    "P4_Finance": """# Daily Briefing — Markets & Finance
Search: WSJ, Bloomberg, Reuters, Financial Times, Yahoo Finance
Topics: index moves >1%, Fed/ECB/central bank signals, major earnings surprises, M&A, crypto if significant
Time window: {time_window}
Rules:
1. English sources ONLY
2. If no significant news, return "No major updates" — never fabricate
3. Focus on significant market movements only (>1%)
4. Max 3-5 items
{dedup_section}
Output format:
1. **[Topic headline]**
   - What: [1-2 sentence summary]
   - Why it matters: [brief impact]
   - Source: [Publication](URL)"""
                }
            }
        },
        "briefings": {
            "morning": {"name": "早间版", "time": "09:00", "timezone": "America/Los_Angeles", "audio_first": True},
            "afternoon": {"name": "下午版", "time": "13:00", "timezone": "America/Los_Angeles", "audio_first": True},
            "evening": {"name": "晚间版", "time": "19:00", "timezone": "America/Los_Angeles", "audio_first": True},
            "night": {"name": "深夜版", "time": "23:00", "timezone": "America/Los_Angeles", "audio_first": True}
        },
        "quality": {
            "signal_threshold": 5,
            "min_p2_p3_count": 1,
            "max_per_author": 2,
            "min_diversity": 3,
            "exclude_categories": ["sports", "entertainment", "ads"]
        },
        "trust_levels": {
            "authoritative": {"name": "权威事实", "emoji": "🏛️", "score": 5},
            "professional": {"name": "专业评论", "emoji": "📊", "score": 4},
            "community": {"name": "社区热议", "emoji": "🔥", "score": 3},
            "personal": {"name": "个人观点", "emoji": "💭", "score": 2},
            "rumor": {"name": "酒馆传闻", "emoji": "🍺", "score": 1}
        },
        "output": {
            "text": {
                "min_items": 10,
                "max_items": 30,
                "max_chars_per_item": 200,
                "separator": "\n\n—-\n\n",
                "divider": "——————————————————"
            },
            "audio": {
                "language": "zh-CN",
                "max_duration": 300,
                "max_chars": 1500,
                "intro_template": "这里是 Varys Spider 情报简报。{date} 太平洋时间 {time}，{edition}。",
                "outro_template": "感谢收听，我们{next_edition}再见。",
                "remove_patterns": [r'https?://[^\s]+'],
                "keep_english": ["GPT", "API", "LLM", "AI", "OpenAI", "H1B", "OPT", "CEO", "CTO"],
                "pronunciation": {
                    "GPT": "G-P-T", "API": "A-P-I", "LLM": "L-L-M",
                    "CEO": "C-E-O", "CTO": "C-T-O", "H1B": "H-1-B", "OPT": "O-P-T"
                }
            }
        },
        "cache": {
            "raw": "cache/raw",
            "processed": "cache/processed",
            "output": "cache/output",
            "ttl_hours": 24
        }
    }
