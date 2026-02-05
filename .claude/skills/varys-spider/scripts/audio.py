"""Generate audio using Microsoft Edge TTS (free) via command line"""
import subprocess
import os
from pathlib import Path
from typing import Optional, Dict


def generate_audio(script: str, edition: str, timestamp: str, config: Dict) -> Optional[Path]:
    """Generate MP3 from TTS script using Edge TTS CLI (zh-CN-XiaoxiaoNeural for Chinese)"""
    
    # Save script to temp file
    cache_dir = Path(config["cache"]["output"])
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    script_path = cache_dir / f"{edition}_{timestamp}_tts.txt"
    audio_path = cache_dir / f"{edition}_{timestamp}.mp3"
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)
    
    # Use edge-tts CLI with Chinese voice
    try:
        result = subprocess.run(
            [
                "edge-tts",
                "--voice", "zh-CN-XiaoxiaoNeural",
                "--file", str(script_path),
                "--write-media", str(audio_path)
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0 and audio_path.exists() and audio_path.stat().st_size > 1000:
            print(f"   ✅ Audio generated: {audio_path}")
            return audio_path
        else:
            error_msg = result.stderr[:200] if result.stderr else 'Unknown error'
            print(f"   ⚠️ Edge TTS failed: {error_msg}")
            
    except Exception as e:
        print(f"   ⚠️ TTS exception: {e}")
    
    print("   💡 Audio generation skipped. Install edge-tts: pip3 install edge-tts")
    return None
