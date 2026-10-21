#!/usr/bin/env python3
"""PostToolUse(Write|Edit) hook, async: rebuild the component index after a .swift
file changes. Produces no context output."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sco_common as sco  # noqa: E402


def main():
    payload = sco.read_stdin_json()
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not path.endswith(".swift"):
        return
    root = sco.project_root(payload)
    try:
        sco.write_index(root, sco.build_index(root))
    except Exception:
        pass


if __name__ == "__main__":
    main()
