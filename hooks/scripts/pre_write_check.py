#!/usr/bin/env python3
"""PreToolUse(Write) hook: when a new .swift file declares UI types, compare them
against the component index. Exact duplicate type name elsewhere -> deny (it would
not compile and signals a missed reuse). Near matches -> inject candidates as context."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sco_common as sco  # noqa: E402

STOP_TOKENS = {"view", "style", "modifier", "screen", "the", "and", "with"}


def main():
    payload = sco.read_stdin_json()
    if payload.get("tool_name") != "Write":
        return
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""
    content = tool_input.get("content") or ""
    if not file_path.endswith(".swift") or not content:
        return
    root = sco.project_root(payload)
    index = sco.load_index(root)
    if index is None:
        sco.emit({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "No component index found. Before adding UI code, run "
                                 "`python3 \"$CLAUDE_PLUGIN_ROOT/hooks/scripts/reindex.py\"` or /swiftui-context-optimiser:init-project."}})
        return

    try:
        rel_new = str(Path(file_path).resolve().relative_to(root.resolve()))
    except Exception:
        rel_new = file_path

    declared = []
    for m in sco.DECL_RE.finditer(content):
        protos = [p.strip().split("<")[0] for p in m.group(3).split(",")]
        if any(p in sco.UI_PROTOCOLS for p in protos):
            declared.append(m.group(2))
    for m in sco.OBSERVABLE_RE.finditer(content):
        declared.append(m.group(1))
    if not declared:
        return

    by_name = {}
    for name, kind, rel in index:
        by_name.setdefault(name.rstrip("()"), []).append((kind, rel))

    exact = []
    for name in declared:
        for kind, rel in by_name.get(name, []):
            if rel != rel_new:
                exact.append(f"{name} ({kind}) already exists at {rel}")
    if exact:
        sco.emit({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Duplicate type: " + "; ".join(exact)
            + ". Reuse or extend the existing type instead of creating a new one. If a second type is truly needed, pick a distinct name and explain why reuse is not possible."}})
        return

    hints = []
    for name in declared:
        toks = set(sco.split_camel(name)) - STOP_TOKENS
        if not toks:
            continue
        scored = []
        for existing, kind, rel in index:
            if rel == rel_new:
                continue
            etoks = set(sco.split_camel(existing.rstrip("()"))) - STOP_TOKENS
            shared = toks & etoks
            if shared:
                scored.append((len(shared) / max(len(toks), 1), existing, kind, rel))
        scored.sort(reverse=True)
        top = [f"{e} ({k}, {r})" for s, e, k, r in scored[:5] if s >= 0.5]
        if top:
            hints.append(f"Possible existing matches for {name}: " + "; ".join(top))
    if hints:
        sco.emit({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "additionalContext": "Reuse check: " + " | ".join(hints)
            + ". If any of these covers the need, stop and reuse or extend it; otherwise continue."}})


if __name__ == "__main__":
    main()
