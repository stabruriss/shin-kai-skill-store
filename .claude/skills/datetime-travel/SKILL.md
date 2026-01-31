---
name: datetime-travel
description: Time-aware assistant with automatic datetime checking and travel timezone switching. Use when (1) User asks about current events, news, "today", "now", or any time-sensitive topics that require knowing the exact date/time, (2) User mentions traveling to a different city/country and wants timezone switching, (3) User says things like "我到了北京", "I'm in Tokyo", "人在纽约" indicating location change, (4) Agent needs to provide time context before answering questions about schedules, deadlines, or current affairs.
---

# Datetime Travel Skill

Helps agents stay time-aware and handle timezone switching when users travel.

## Features

1. **Auto-detect time-sensitive queries** - Reminds agent to check current time
2. **Travel mode switching** - One-command timezone change when user mentions travel
3. **Dual timezone display** - Shows both local time and home time
4. **Persistent state** - Remembers timezone across sessions

## Scripts

### `datetime` - Get current time
```bash
# Get time in current timezone (follows travel mode)
~/.openclaw/tools/datetime

# Get time in specific formats
~/.openclaw/tools/datetime full      # Full format with timezone
~/.openclaw/tools/datetime pt        # Force Pacific Time (home)
~/.openclaw/tools/datetime travel    # Show current travel location time
~/.openclaw/tools/datetime iso       # ISO format
~/.openclaw/tools/datetime unix      # Unix timestamp
```

### `travel` - Switch timezones
```bash
# Travel to a city (auto-detects timezone)
travel beijing      # Switch to Beijing/Shanghai time (UTC+8)
travel nyc          # Switch to New York time
travel tokyo        # Switch to Tokyo time
travel london       # Switch to London time

# Check current status
travel              # Show current timezone + home timezone
travel status       # Same as above

# Return home
travel home         # Return to Pacific Time (default home)
travel reset        # Same as above

# List supported cities
travel list
```

## Auto-Detection Patterns

When user messages contain these patterns, agent should check datetime:
- "今天..." / "Today..."
- "现在..." / "Now..."
- "最近..." / "Recently..."
- "Latest..." / "最新..."
- "What's happening..."
- Any question about current events, news, schedules

When user messages indicate travel:
- "我到了[城市]" / "I'm in [city]"
- "人在[城市]" / "Currently in [city]"
- "现在在[城市]" / "Now at [city]"
- "到了[城市]" / "Arrived at [city]"

## Usage Examples

### Example 1: Time-sensitive query
**User**: "今天有什么新闻？"

**Agent action**:
1. Detect time-sensitive keyword "今天"
2. Run `~/.openclaw/tools/datetime full`
3. Answer with current date context: "今天是2026年1月31日，新闻有..."

### Example 2: Travel detection
**User**: "我到了北京"

**Agent action**:
1. Detect travel pattern "到了" + city
2. Run `travel beijing`
3. Confirm: "已切换到北京时区 (UTC+8)，现在北京时间是..."

### Example 3: Return home
**User**: "我回湾区了"

**Agent action**:
1. Detect "回" + home location
2. Run `travel home`
3. Confirm: "欢迎回家！已切换回 Pacific Time"

## Supported Cities

| Command | City | Timezone |
|---------|------|----------|
| `travel beijing` / `shanghai` | 北京/上海 | Asia/Shanghai (UTC+8) |
| `travel tokyo` | 东京 | Asia/Tokyo (UTC+9) |
| `travel nyc` / `newyork` | 纽约 | America/New_York (UTC-5/4) |
| `travel london` | 伦敦 | Europe/London (UTC+0/1) |
| `travel paris` | 巴黎 | Europe/Paris (UTC+1/2) |
| `travel sydney` | 悉尼 | Australia/Sydney (UTC+10/11) |
| `travel singapore` | 新加坡 | Asia/Singapore (UTC+8) |
| `travel hk` / `hongkong` | 香港 | Asia/Hong_Kong (UTC+8) |
| `travel taipei` | 台北 | Asia/Taipei (UTC+8) |
| `travel dubai` | 迪拜 | Asia/Dubai (UTC+4) |
| `travel berlin` | 柏林 | Europe/Berlin (UTC+1/2) |
| `travel toronto` | 多伦多 | America/Toronto (UTC-5/4) |
| `travel vancouver` | 温哥华 | America/Vancouver (UTC-8/7) |
| `travel chicago` | 芝加哥 | America/Chicago (UTC-6/5) |
| `travel sf` / `sanfrancisco` | 旧金山 | America/Los_Angeles (UTC-8/7) |

Run `travel list` for complete list.

## Configuration

### Default Home Timezone
Edit the script to change default home timezone:
```bash
# In ~/.openclaw/tools/travel
HOME_TZ="America/Los_Angeles"  # Change this
```

### Adding New Cities
Edit `CITY_TZ` array in `~/.openclaw/tools/travel`:
```bash
declare -A CITY_TZ=(
    ...
    ["yourcity"]="Your/Timezone"
)
```

## State Files

- `~/.openclaw/.travel_state` - Current travel timezone
- `~/.openclaw/AGENTS.md` - Time awareness rules for agent

## Notes

- Daylight saving time is handled automatically by system timezone database
- Travel state persists across sessions
- Use `datetime pt` to force home timezone regardless of travel mode
