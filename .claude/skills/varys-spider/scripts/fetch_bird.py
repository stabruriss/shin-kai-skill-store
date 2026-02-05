"""Fetch data from Bird (Twitter/X) using bird CLI"""
import os
import json
import subprocess
from datetime import datetime
from typing import List, Dict
from pathlib import Path


def fetch_bird_data(config: Dict) -> List[Dict]:
    """Fetch tweets from focus accounts using bird CLI"""
    bird_config = config["sources"]["bird"]
    
    if not bird_config.get("enabled", False):
        return []
    
    focus_accounts = bird_config.get("focus_accounts", [])
    test_limit = 6  # Limit total accounts for concise briefing
    accounts_to_fetch = focus_accounts[:test_limit]
    
    print(f"   🐦 Fetching from {len(accounts_to_fetch)}/{len(focus_accounts)} accounts via bird CLI")
    
    # Check if bird is installed
    try:
        result = subprocess.run(["bird", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("   ⚠️ bird CLI not found. Install: npm install -g @steipete/bird")
            return []
    except FileNotFoundError:
        print("   ⚠️ bird CLI not found. Install: npm install -g @steipete/bird")
        print("   💡 Or use: bunx @steipete/bird")
        return []
    
    all_items = []
    
    # Prepare environment with Twitter cookies
    env = os.environ.copy()
    env["AUTH_TOKEN"] = os.environ.get("BIRD_AUTH_TOKEN", os.environ.get("AUTH_TOKEN", ""))
    env["CT0"] = os.environ.get("BIRD_CT0", os.environ.get("CT0", ""))
    
    for username in accounts_to_fetch:
        try:
            username = username.lstrip("@")
            items = fetch_user_tweets_bird(username, count=2, env=env)
            
            if items:
                all_items.extend(items)
                print(f"      ✅ {username}: {len(items)} tweets")
            else:
                print(f"      ℹ️ {username}: no tweets")
                
        except Exception as e:
            print(f"      ❌ {username}: {str(e)[:60]}")
    
    print(f"   🐦 Total Bird items: {len(all_items)}")
    return all_items


def fetch_user_tweets_bird(username: str, count: int = 10, env: dict = None) -> List[Dict]:
    """Fetch user tweets using bird CLI"""
    items = []
    
    try:
        # Use bird to get user tweets
        # bird user-tweets USERNAME -n COUNT --json
        result = subprocess.run(
            ["bird", "user-tweets", username, "-n", str(count), "--json"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            if "not logged in" in error_msg.lower() or "auth" in error_msg.lower():
                print(f"      ⚠️ {username}: Not authenticated. Run 'bird whoami' to check.")
            else:
                print(f"      ⚠️ {username}: {error_msg[:100]}")
            return []
        
        # Parse JSON output
        tweets = json.loads(result.stdout)
        
        if isinstance(tweets, list):
            for tweet in tweets[:count]:
                item = {
                    "id": f"bird_{tweet.get('id', '')}",
                    "source": "bird",
                    "priority": "P1",
                    "author": username,
                    "content": tweet.get("text", tweet.get("fullText", "")),
                    "url": f"https://x.com/{username}/status/{tweet.get('id', '')}",
                    "timestamp": tweet.get("createdAt", datetime.now().isoformat()),
                    "citations": [f"https://x.com/{username}/status/{tweet.get('id', '')}"],
                    "raw": tweet
                }
                items.append(item)
        
    except json.JSONDecodeError as e:
        print(f"      ⚠️ {username}: JSON parse error - {e}")
    except Exception as e:
        print(f"      ❌ {username}: {e}")
    
    return items
