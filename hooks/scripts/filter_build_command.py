#!/usr/bin/env python3
"""PreToolUse(Bash) hook: pipe xcodebuild / swift build / swift test output through
build_filter.py so only errors, warnings, test failures and the final verdict reach
the context. Leaves commands alone when they already pipe through a formatter."""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sco_common as sco  # noqa: E402

BUILD_RE = re.compile(r"(^|[;&|]\s*)(xcrun\s+)?(xcodebuild|swift\s+(build|test|run))\b")
ALREADY = ("xcbeautify", "xcpretty", "build_filter.py", "| grep", "| rg", "| tail", "| head", "| tee")


def main():
    payload = sco.read_stdin_json()
    if payload.get("tool_name") != "Bash":
        return
    tool_input = payload.get("tool_input") or {}
    cmd = tool_input.get("command") or ""
    if not BUILD_RE.search(cmd) or any(tok in cmd for tok in ALREADY):
        return
    if "\n" in cmd.strip():
        return  # multi-line scripts: do not rewrite, too easy to break
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or str(Path(__file__).resolve().parents[2])
    filt = f'python3 "{plugin_root}/hooks/scripts/build_filter.py"'
    new_cmd = f"set -o pipefail; {cmd} 2>&1 | {filt}"
    updated = dict(tool_input)
    updated["command"] = new_cmd
    sco.emit({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "updatedInput": updated,
        "additionalContext": "Build output is filtered to errors, warnings and test results. Rerun with `| cat` appended if full logs are needed."}})


if __name__ == "__main__":
    main()
