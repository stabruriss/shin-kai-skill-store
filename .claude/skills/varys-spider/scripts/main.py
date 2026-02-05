#!/usr/bin/env python3
"""
Varys Spider - Main Entry Point
Hybrid intelligence briefing system combining Bird (Twitter) and Perplexity

Output: Audio first (Chinese TTS), then text digest with inline citations
"""

import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

# Add skill directory to path
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR))

from scripts.config_loader import load_config
from scripts.fetch_bird import fetch_bird_data
from scripts.fetch_perplexity import fetch_perplexity_data
from scripts.filter import filter_items
from scripts.trust_level import classify_trust_level
from scripts.signal import score_signal
from scripts.format import format_text_digest, format_tts_script
from scripts.audio import generate_audio
from scripts.deliver import deliver_to_telegram


def main():
    parser = argparse.ArgumentParser(description="Varys Spider Intelligence Briefing")
    parser.add_argument("--edition", choices=["morning", "afternoon", "evening", "night"],
                       default="morning", help="Briefing edition")
    parser.add_argument("--output", choices=["audio", "text", "both"],
                       default="both", help="Output type")
    parser.add_argument("--dry-run", action="store_true",
                       help="Generate without sending")
    parser.add_argument("--target", default="8509139631",
                       help="Telegram chat ID")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    print(f"🕷️ Varys Spider - {args.edition} edition starting...")
    
    # Step 1: Fetch data from both sources
    print("📡 Fetching data...")
    bird_items = fetch_bird_data(config) if config["sources"]["bird"]["enabled"] else []
    perplexity_items = fetch_perplexity_data(config, args.edition) if config["sources"]["perplexity"]["enabled"] else []
    
    all_items = bird_items + perplexity_items
    print(f"   Bird: {len(bird_items)} items")
    print(f"   Perplexity: {len(perplexity_items)} items")
    print(f"   Total: {len(all_items)} items")
    
    if not all_items:
        print("⚠️ No data fetched. Exiting.")
        return 1
    
    # Step 2: LLM-based quality filtering
    print("🧹 LLM quality assessment & filtering...")
    filtered_items = filter_items(all_items, config)
    
    # Step 3: Trust level classification (using LLM assessment if available)
    print("🏷️ Classifying trust levels...")
    for item in filtered_items:
        item["trust_level"] = classify_trust_level(item, config)
    
    # Step 4: Signal scoring
    print("📊 Scoring signals...")
    scored_items = score_signal(filtered_items, config)
    print(f"   After quality gates: {len(scored_items)} items")
    
    if not scored_items:
        print("⚠️ No items passed quality gates.")
        return 1
    
    # Step 5: Format output
    print("📝 Formatting output...")
    edition_name = config["briefings"][args.edition]["name"]
    
    # Text digest (with inline citations - translation handled by calling agent)
    text_digest = format_text_digest(scored_items, edition_name, config)
    
    # TTS script (Chinese-focused)
    tts_script = format_tts_script(scored_items, edition_name, config)
    
    # Save to cache
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_dir = Path(config["cache"]["output"])
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    text_path = cache_dir / f"{args.edition}_{timestamp}.txt"
    tts_path = cache_dir / f"{args.edition}_{timestamp}_tts.txt"
    
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_digest)
    with open(tts_path, "w", encoding="utf-8") as f:
        f.write(tts_script)
    
    print(f"   Text saved: {text_path}")
    print(f"   TTS script saved: {tts_path}")
    
    # Step 6: Generate audio (ALWAYS generate for briefing)
    audio_path = None
    if args.output in ["audio", "both"]:
        print("🔊 Generating audio (Edge TTS)...")
        audio_path = generate_audio(tts_script, args.edition, timestamp, config)
        if audio_path:
            print(f"   Audio saved: {audio_path}")
    
    # Step 7: Deliver - AUDIO FIRST, then text
    if not args.dry_run:
        print("📤 Delivering to Telegram (audio first, then text)...")
        deliver_to_telegram(
            text_digest=text_digest,
            audio_path=audio_path,
            target=args.target,
            edition=args.edition,
            audio_first=True,  # Always audio first
            channel="telegram"
        )
        print("✅ Delivery complete!")
    else:
        print("🧪 Dry run - not sending")
        print(f"   Would send audio: {audio_path is not None}")
        print(f"   Text length: {len(text_digest)} chars")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
