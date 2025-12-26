# Claude Skills

Custom skills for Claude AI - extending capabilities with specialized workflows and tools.

## Available Skills

### transcript-recovery
Recover full conversation history after context compaction. Use when context window is compacted and Claude needs to access earlier parts of the conversation.

**Usage:**
```bash
# In Claude container
python3 get_transcript.py --list           # List transcripts
python3 get_transcript.py --all --messages  # Full history
python3 get_transcript.py --search "topic"  # Search
```

## Structure

Each skill follows the standard structure:
```
skill-name/
├── SKILL.md           # Documentation and metadata
└── scripts/           # Executable scripts
```

## Installation

Clone and use scripts directly in Claude's container environment.
