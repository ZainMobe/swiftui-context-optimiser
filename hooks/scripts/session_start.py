#!/usr/bin/env python3
"""SessionStart hook: inject the compact rule block for Swift projects, refresh the
component index, and nudge for a memory digest when notes have grown.
Emits nothing for non-Swift projects so no tokens are spent there."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sco_common as sco  # noqa: E402

RULES = """SwiftUI Context Optimiser rules (these override conflicting skill guidance, including SwiftUI Pro's "add comments where logic is not self-evident"):
1. Reuse first. Before creating any View, ViewModifier, style, shape, helper or model, check .claude/swiftui-components.md. If a match or near-match exists, reuse or extend it. Only when nothing fits, create it, and make it reusable (parameters, no hard-coded copy). Use the component-finder agent when the index is inconclusive.
2. No code comments, doc comments or MARK lines unless the developer asks.
3. Ask, do not guess. If a requirement, design, API shape or edge case is unclear, ask one precise question before writing code.
4. Match existing conventions exactly: naming, folder layout, state management style, formatting. Read .claude/conventions.md if present.
5. Context thrift: Grep/Glob before Read; read only the line ranges needed; never re-read an unchanged file; delegate broad exploration to the Explore or component-finder subagent; reply briefly, no recaps or summaries of work done.
6. Run SwiftUI Pro review only when asked, not after every edit.
7. Keep CLAUDE.md and auto-memory lean: record decisions and conventions, not task logs."""

CLAUDE_MD_LIMIT = 80
MEMORY_LIMIT_LINES = 120
MEMORY_LIMIT_BYTES = 25_000


def memory_dir_for(root: Path):
    home = Path.home()
    slug = "".join(c if c.isalnum() else "-" for c in str(root))
    candidate = home / ".claude" / "projects" / slug / "memory"
    return candidate if candidate.exists() else None


def digest_nudge(root: Path):
    reasons = []
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        n = sum(1 for _ in claude_md.open(encoding="utf-8", errors="ignore"))
        if n > CLAUDE_MD_LIMIT:
            reasons.append(f"CLAUDE.md has {n} lines (limit {CLAUDE_MD_LIMIT})")
    mem = memory_dir_for(root)
    if mem:
        total = sum(p.stat().st_size for p in mem.rglob("*") if p.is_file())
        index = mem / "MEMORY.md"
        if index.exists():
            n = sum(1 for _ in index.open(encoding="utf-8", errors="ignore"))
            if n > MEMORY_LIMIT_LINES:
                reasons.append(f"MEMORY.md has {n} lines (limit {MEMORY_LIMIT_LINES})")
        if total > MEMORY_LIMIT_BYTES:
            reasons.append(f"auto-memory is {total // 1024} KB (limit {MEMORY_LIMIT_BYTES // 1024} KB)")
    if not reasons:
        return ""
    return ("\nMemory digest due: " + "; ".join(reasons)
            + ". Offer to run /swiftui-context-optimiser:digest once, then continue.")


def reset_read_state(payload):
    base = payload.get("scratchpad_dir") or os.environ.get("TMPDIR") or "/tmp"
    sid = payload.get("session_id") or "nosession"
    p = Path(base) / f"sco_reads_{sid}.json"
    try:
        p.unlink()
    except OSError:
        pass


def main():
    payload = sco.read_stdin_json()
    if payload.get("source") in ("compact", "clear"):
        reset_read_state(payload)
    root = sco.project_root(payload)
    if not sco.is_swift_project(root):
        return
    try:
        entries = sco.build_index(root)
        sco.write_index(root, entries)
        index_note = f"\nComponent index: .claude/swiftui-components.md ({len(entries)} entries)."
    except Exception as e:  # never fail the session over the index
        index_note = f"\nComponent index unavailable ({e.__class__.__name__})."
    conventions = ""
    if (root / sco.CONVENTIONS_REL).exists():
        conventions = "\nConventions file: .claude/conventions.md (read before writing new code)."
    else:
        conventions = "\nNo .claude/conventions.md yet; suggest /swiftui-context-optimiser:learn-conventions once if the project has existing code."
    context = RULES + index_note + conventions + digest_nudge(root)
    sco.emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}})


if __name__ == "__main__":
    main()
