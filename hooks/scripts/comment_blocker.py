#!/usr/bin/env python3
"""PreToolUse(Write|Edit|MultiEdit) hook: deny Swift writes that add comment lines.
Allowed: swiftlint and swift-tools-version directives, shebangs, and comments that were
already present in the text being replaced (Edit old_string)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sco_common as sco  # noqa: E402

COMMENT_RE = re.compile(r"^\s*(//|/\*)")
ALLOWED_RE = re.compile(
    r"^\s*//\s*(swiftlint|swift-tools-version|swiftformat|periphery|sourcery|TODO:\s*ASKED|@preconcurrency)",
    re.I,
)


def comment_lines(text: str):
    out = []
    for line in text.splitlines():
        if COMMENT_RE.match(line) and not ALLOWED_RE.match(line):
            out.append(line.strip())
    return out


def main():
    payload = sco.read_stdin_json()
    tool = payload.get("tool_name")
    ti = payload.get("tool_input") or {}
    path = ti.get("file_path") or ""
    if not path.endswith(".swift"):
        return
    added = []
    if tool == "Write":
        added = comment_lines(ti.get("content") or "")
    elif tool == "Edit":
        before = set(comment_lines(ti.get("old_string") or ""))
        added = [c for c in comment_lines(ti.get("new_string") or "") if c not in before]
    elif tool == "MultiEdit":
        for e in ti.get("edits") or []:
            before = set(comment_lines(e.get("old_string") or ""))
            added += [c for c in comment_lines(e.get("new_string") or "") if c not in before]
    if not added:
        return
    sample = "; ".join(a[:60] for a in added[:3])
    sco.emit({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"Project rule: no comments or MARK lines unless the developer asks. "
        f"{len(added)} comment line(s) found, e.g. {sample}. Remove them and retry. "
        f"If the developer explicitly asked for comments in this file, say so and retry; the hook does not know."}})


if __name__ == "__main__":
    main()
