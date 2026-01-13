# Shin-Kai Skill Store

A collection of Claude Code skills for enhancing productivity.

## Available Skills

| Skill | Description |
|-------|-------------|
| [prd-writing](.claude/skills/prd-writing/) | Helps PMs write clear, developer-friendly PRDs with dual-format output |

## Quick Install

Copy the `.claude` directory to your project root:

```bash
# Clone this repo
git clone https://github.com/YOUR_USERNAME/shin-kai-skill-store.git

# Copy all skills to your project
cp -r shin-kai-skill-store/.claude /path/to/your-project/

# Or copy a specific skill
cp -r shin-kai-skill-store/.claude/skills/prd-writing /path/to/your-project/.claude/skills/
```

## Usage

In Claude Code, invoke skills using:

```
/prd-writing
```

## Update

```bash
# Re-clone and copy to get the latest version
git clone https://github.com/YOUR_USERNAME/shin-kai-skill-store.git
cp -r shin-kai-skill-store/.claude /path/to/your-project/
```

## Contributing

To add a new skill:

1. Create a directory under `.claude/skills/[skill-name]/`
2. Add a `SKILL.md` file with the skill definition
3. Update this README with the skill description
4. Submit a PR

## License

MIT
