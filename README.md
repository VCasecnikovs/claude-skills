# Claude Skills

Custom skills for Claude AI - extending capabilities with specialized workflows and tools.

## Installation

1. Download the `.skill` file from [Releases](https://github.com/VCasecnikovs/claude-skills/releases)
2. In Claude.ai, go to Settings → Skills
3. Upload the `.skill` file
4. Skill appears in `/mnt/skills/user/` and is ready to use

## Available Skills

### transcript-recovery

Recover full conversation history after context compaction.

**Triggers:**
- Context window is compacted
- User asks about previous discussions
- Need to continue work from earlier in conversation

**Usage (automatic after install):**
```bash
python3 /mnt/skills/user/transcript-recovery/scripts/get_transcript.py --list
python3 /mnt/skills/user/transcript-recovery/scripts/get_transcript.py --all --messages
python3 /mnt/skills/user/transcript-recovery/scripts/get_transcript.py --search "topic"
```

## Building Skills

Each skill follows the structure:
```
skill-name/
├── SKILL.md           # Documentation with YAML frontmatter
└── scripts/           # Executable scripts
```

To package:
```bash
python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py ./skill-name
```
