#!/usr/bin/env python3
"""
Transcript retrieval tool for Claude conversations.
Recovers full chat history from /mnt/transcripts/ after context compaction.
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

TRANSCRIPTS_DIR = Path("/mnt/transcripts")

def decode_unicode_escapes(content: str) -> str:
    """Convert \\uXXXX escapes to readable UTF-8."""
    def replace(match):
        codepoint = int(match.group(1), 16)
        if 0xD800 <= codepoint <= 0xDFFF:
            return match.group(0)
        return chr(codepoint)
    decoded = re.sub(r'\\u([0-9a-fA-F]{4})', replace, content)
    return decoded.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='replace')

def get_transcript_list() -> list[dict]:
    """Get list of all transcripts with metadata."""
    transcripts = []
    for f in sorted(TRANSCRIPTS_DIR.glob("*.txt")):
        if f.name == "journal.txt":
            continue
        stat = f.stat()
        transcripts.append({
            "name": f.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "path": str(f)
        })
    return transcripts

def get_current_transcript() -> Path | None:
    """Get the most recent transcript file."""
    transcripts = get_transcript_list()
    if not transcripts:
        return None
    return Path(sorted(transcripts, key=lambda x: x["name"], reverse=True)[0]["path"])

def read_transcript(path: Path, tail: int = None) -> str:
    """Read and decode a transcript file."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    decoded = decode_unicode_escapes(content)
    if tail:
        lines = decoded.split('\n')
        return '\n'.join(lines[-tail:])
    return decoded

def search_transcripts(query: str) -> list[dict]:
    """Search across all transcripts."""
    results = []
    query_lower = query.lower()
    for t in get_transcript_list():
        content = read_transcript(Path(t["path"]))
        if query_lower in content.lower():
            matches = []
            for i, line in enumerate(content.split('\n')):
                if query_lower in line.lower():
                    matches.append({"line": i + 1, "text": line[:200]})
            results.append({"file": t["name"], "matches": matches[:10]})
    return results

def combine_all_transcripts() -> str:
    """Combine all transcripts chronologically."""
    combined = []
    for t in sorted(get_transcript_list(), key=lambda x: x["name"]):
        combined.append(f"\n{'='*80}")
        combined.append(f"=== FILE: {t['name']} ===")
        combined.append(f"{'='*80}\n")
        combined.append(read_transcript(Path(t["path"])))
    return '\n'.join(combined)

def extract_messages(content: str) -> list[dict]:
    """Extract human/assistant messages from transcript JSON."""
    messages = []
    parts = re.split(r'\n(Human|Assistant):\nContent:\n', content)
    for i in range(1, len(parts), 2):
        role = parts[i] if i < len(parts) else None
        json_content = parts[i+1] if i+1 < len(parts) else None
        if role and json_content:
            try:
                match = re.search(r'\[[\s\S]*?\n\]', json_content)
                if match:
                    data = json.loads(match.group())
                    for item in data:
                        if item.get("type") == "text" and item.get("text"):
                            text = item["text"].strip()
                            if text and text != " ":
                                messages.append({"role": role.lower(), "text": text})
            except json.JSONDecodeError:
                pass
    return messages

def format_messages(messages: list[dict], max_length: int = None) -> str:
    """Format messages for readable output."""
    output = []
    for msg in messages:
        role = "HUMAN" if msg["role"] == "human" else "CLAUDE"
        text = msg["text"]
        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."
        output.append(f"\n[{role}]:\n{text}\n")
    return '\n'.join(output)

def main():
    parser = argparse.ArgumentParser(description="Retrieve Claude conversation transcripts")
    parser.add_argument("--list", "-l", action="store_true", help="List all transcripts")
    parser.add_argument("--all", "-a", action="store_true", help="Combine all transcripts")
    parser.add_argument("--file", "-f", type=str, help="Specific transcript file")
    parser.add_argument("--search", "-s", type=str, help="Search query")
    parser.add_argument("--tail", "-t", type=int, help="Last N lines only")
    parser.add_argument("--messages", "-m", action="store_true", help="Extract messages only")
    parser.add_argument("--output", "-o", type=str, help="Output file path")
    parser.add_argument("--truncate", type=int, default=None, help="Truncate messages to N chars")
    args = parser.parse_args()
    
    result = ""
    
    if args.list:
        transcripts = get_transcript_list()
        print(f"Found {len(transcripts)} transcripts:\n")
        for t in transcripts:
            print(f"  {t['name']} ({t['size']/1024:.1f} KB)")
        return
    elif args.search:
        results = search_transcripts(args.search)
        if not results:
            print(f"No matches for: {args.search}")
            return
        for r in results:
            print(f"=== {r['file']} ===")
            for m in r["matches"]:
                print(f"  L{m['line']}: {m['text'][:80]}...")
        return
    elif args.all:
        result = combine_all_transcripts()
    elif args.file:
        path = TRANSCRIPTS_DIR / args.file
        if not path.exists():
            print(f"Error: {args.file} not found")
            sys.exit(1)
        result = read_transcript(path, args.tail)
    else:
        current = get_current_transcript()
        if not current:
            print("No transcripts found")
            sys.exit(1)
        print(f"Current: {current.name}\n", file=sys.stderr)
        result = read_transcript(current, args.tail)
    
    if args.messages and result:
        messages = extract_messages(result)
        result = format_messages(messages, args.truncate)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Saved: {args.output}")
    elif result:
        print(result)

if __name__ == "__main__":
    main()
