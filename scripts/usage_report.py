#!/usr/bin/env python3
"""Summarise where context went in the newest Claude Code transcript for this project.
Usage: python3 usage_report.py [project-root]
Reads ~/.claude/projects/<slug>/*.jsonl (newest first), counts tool calls and the size
of tool results, and lists files read more than once. Sizes are characters; divide
by roughly 4 for a token estimate."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def slug_for(root: Path) -> str:
    return "".join(c if c.isalnum() else "-" for c in str(root))


def newest_transcript(root: Path):
    d = Path.home() / ".claude" / "projects" / slug_for(root)
    if not d.exists():
        return None
    files = sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def iter_blocks(path: Path):
    with path.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            msg = rec.get("message") or {}
            content = msg.get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        yield rec.get("type"), block


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    path = newest_transcript(root)
    if not path:
        print(f"No transcript found for {root}")
        return
    calls = Counter()
    result_chars = Counter()
    reads = Counter()
    pending = {}
    biggest = []
    text_chars = 0
    for kind, block in iter_blocks(path):
        t = block.get("type")
        if t == "tool_use":
            name = block.get("name", "?")
            calls[name] += 1
            pending[block.get("id")] = (name, block.get("input") or {})
            if name == "Read":
                reads[(block.get("input") or {}).get("file_path", "?")] += 1
        elif t == "tool_result":
            content = block.get("content")
            size = len(content) if isinstance(content, str) else sum(
                len(c.get("text", "")) for c in content if isinstance(c, dict)) if isinstance(content, list) else 0
            name, inp = pending.get(block.get("tool_use_id"), ("?", {}))
            result_chars[name] += size
            label = inp.get("file_path") or inp.get("command") or inp.get("pattern") or ""
            biggest.append((size, name, str(label)[:80]))
        elif t == "text":
            text_chars += len(block.get("text", ""))

    total_results = sum(result_chars.values())
    print(f"Transcript: {path.name}  ({path.stat().st_size // 1024} KB on disk)")
    print(f"Tool results total: {total_results:,} chars (~{total_results // 4:,} tokens); "
          f"assistant/user text: {text_chars:,} chars")
    print("\nBy tool (calls, result chars):")
    for name, n in calls.most_common():
        print(f"  {name:<22} {n:>4}  {result_chars[name]:>10,}")
    print("\nLargest tool results:")
    for size, name, label in sorted(biggest, reverse=True)[:10]:
        print(f"  {size:>9,}  {name:<10} {label}")
    rereads = [(f, n) for f, n in reads.items() if n > 1]
    if rereads:
        print("\nFiles read more than once (candidates for Grep or line-range reads):")
        for f, n in sorted(rereads, key=lambda x: -x[1])[:10]:
            print(f"  {n}x  {f}")


if __name__ == "__main__":
    main()
