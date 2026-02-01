#!/usr/bin/env python3
"""
check-network.py - Verify Varys Spider's intelligence network
"""

import os
import sys
import subprocess
from pathlib import Path

def check_command(cmd):
    return subprocess.run(f"which {cmd}", shell=True, capture_output=True).returncode == 0

def check_env(var):
    return os.environ.get(var) is not None

def main():
    print("🕷️  Varys Spider - Network Check\n")
    
    # Core
    print("Core Tools:")
    py = sys.version_info >= (3, 8)
    print(f"  {'✅' if py else '❌'} Python 3.8+")
    
    curl = check_command("curl") or check_command("wget")
    print(f"  {'✅' if curl else '❌'} curl/wget")
    
    # Sources
    print("\nIntelligence Sources:")
    
    # Twitter
    bird = check_command("bird")
    twitter_creds = check_env("AUTH_TOKEN") and check_env("CT0")
    if bird and twitter_creds:
        print("  ✅ Twitter/X (bird + credentials)")
    elif bird:
        print("  ⚠️  Twitter/X (bird installed, needs credentials)")
    else:
        print("  ⚠️  Twitter/X (install: brew install steipete/tap/bird)")
    
    # Hacker News - FREE
    print("  ✅ Hacker News API (FREE, no auth)")
    
    # Reddit
    reddit_creds = check_env("REDDIT_CLIENT_ID") and check_env("REDDIT_SECRET")
    if reddit_creds:
        print("  ✅ Reddit API")
    else:
        print("  ⚠️  Reddit API (optional, needs credentials)")
    
    # RSS
    print("  ✅ RSS Feeds (Reuters, BBC, AP - FREE)")
    
    # NewsAPI
    if check_env("NEWSAPI_KEY"):
        print("  ✅ NewsAPI")
    else:
        print("  ⚠️  NewsAPI (optional, get free key at newsapi.org)")
    
    # GitHub
    print("  ✅ GitHub Trending (FREE)")
    
    # Config
    print("\nConfiguration:")
    web = Path.home() / ".openclaw/varys-spider/web.json"
    if web.exists():
        print("  ✅ Web configuration initialized")
    else:
        print(f"  ❌ Web not initialized (run: varys-spider init)")
    
    print("\n" + "="*50)
    print("🕷️  The Spider can work with FREE sources immediately:")
    print("   - RSS news feeds")
    print("   - Hacker News")  
    print("   - GitHub Trending")
    print("\n   Optional enhancements:")
    print("   - Twitter (for social monitoring)")
    print("   - NewsAPI (for unified search)")
    print("   - Reddit (for community intel)")

if __name__ == "__main__":
    main()
