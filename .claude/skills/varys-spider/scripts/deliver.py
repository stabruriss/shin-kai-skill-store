"""Deliver content to Telegram - Audio first, then text"""
import subprocess
import json
from pathlib import Path
from typing import Optional


def deliver_to_telegram(
    text_digest: str,
    audio_path: Optional[Path],
    target: str,
    edition: str,
    audio_first: bool = True,
    channel: str = "telegram"
):
    """Deliver briefing to Telegram channel - AUDIO FIRST, then text"""
    
    # Step 1: Send audio FIRST (if available)
    if audio_path and audio_path.exists():
        print("   🔊 Sending audio first...")
        send_audio(audio_path, target, edition, channel)
    else:
        print("   ℹ️ No audio to send")
    
    # Step 2: Send text (after audio)
    print("   📝 Sending text...")
    send_text(text_digest, target, channel)


def send_audio(audio_path: Path, target: str, edition: str, channel: str = "telegram"):
    """Send audio file via Telegram as voice message"""
    try:
        # For Telegram, MP3 files sent via --media are treated as voice messages
        result = subprocess.run(
            [
                "openclaw", "message", "send",
                "--channel", channel,
                "--target", target,
                "--media", str(audio_path)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"   ⚠️ Audio send error: {result.stderr[:200]}")
        else:
            print(f"   ✅ Audio sent successfully")
            
    except Exception as e:
        print(f"   ⚠️ Audio send exception: {e}")


def send_text(text: str, target: str, channel: str = "telegram"):
    """Send text, splitting if necessary - MAX 3 chunks (total 4 with audio)"""
    # Telegram message limit is ~4096 chars
    max_len = 4000
    MAX_CHUNKS = 3  # Audio + 3 text = 4 total messages max
    
    if len(text) <= max_len:
        _send_text_chunk(text, target, 1, 1, channel)
    else:
        # Split at paragraph boundaries
        chunks = split_text(text, max_len)
        # Limit to max chunks
        if len(chunks) > MAX_CHUNKS:
            print(f"   ⚠️ Content too long, truncating to {MAX_CHUNKS} parts")
            chunks = chunks[:MAX_CHUNKS]
        total = len(chunks)
        for i, chunk in enumerate(chunks, 1):
            _send_text_chunk(chunk, target, i, total, channel)


def _send_text_chunk(chunk: str, target: str, index: int, total: int, channel: str = "telegram"):
    """Send a single text chunk"""
    header = f"({index}/{total})\n\n" if total > 1 else ""
    message = header + chunk
    
    try:
        result = subprocess.run(
            [
                "openclaw", "message", "send",
                "--channel", channel,
                "--target", target,
                "--message", message
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"   ⚠️ Text send error: {result.stderr[:200]}")
        else:
            print(f"   ✅ Text part {index}/{total} sent")
            
    except Exception as e:
        print(f"   ⚠️ Text send exception: {e}")


def split_text(text: str, max_len: int) -> list:
    """Split text into chunks at paragraph boundaries"""
    chunks = []
    current = ""
    
    # Split by the separator pattern
    paragraphs = text.split("\n\n————\n\n")
    
    for para in paragraphs:
        if len(current) + len(para) + 10 < max_len:
            current += para + "\n\n————\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = para + "\n\n————\n\n"
    
    if current:
        chunks.append(current.strip())
    
    return chunks
