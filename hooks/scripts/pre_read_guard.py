#!/usr/bin/env python3
"""PreToolUse(Read) hook with two guards.
Heavy-file guard: deny reads of generated or build artefacts (pbxproj, Package.resolved,
xcstrings, xcassets Contents.json, DerivedData, .build, Pods) and of long files read
without offset/limit, pointing at Grep or a ranged read instead.
Re-read guard: deny a second full read of a file unchanged since it was last read in this
session. Ranged reads (offset or limit) are always allowed, so Claude can get content back
when it is truly needed."""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sco_common as sco  # noqa: E402

LARGE_FILE_BYTES = 24_000
HEAVY_SUFFIXES = (".pbxproj", "Package.resolved", ".xcstrings", ".xcuserstate", ".xcscheme")
HEAVY_DIRS = ("/DerivedData/", "/.build/", "/Pods/", "/Carthage/", "/.swiftpm/", "/xcuserdata/")
BINARY_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".heic", ".webp", ".svg")


def state_path(payload):
    base = payload.get("scratchpad_dir") or os.environ.get("TMPDIR") or "/tmp"
    sid = payload.get("session_id") or "nosession"
    return Path(base) / f"sco_reads_{sid}.json"


def load_state(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def save_state(p: Path, state):
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state))
    except Exception:
        pass


def deny(reason):
    sco.emit({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason}})


def main():
    payload = sco.read_stdin_json()
    if payload.get("tool_name") != "Read":
        return
    ti = payload.get("tool_input") or {}
    path = ti.get("file_path") or ""
    if not path or path.endswith(BINARY_SUFFIXES):
        return
    ranged = ti.get("offset") is not None or ti.get("limit") is not None
    norm = "/" + path.strip("/") + "/"

    if any(d in norm for d in HEAVY_DIRS):
        deny(f"{path} is a build or dependency artefact. Do not read it; Grep the source tree instead, "
             f"or ask the developer if this file is really needed.")
        return
    if path.endswith(HEAVY_SUFFIXES) or (path.endswith("Contents.json") and ".xcassets" in path):
        if not ranged:
            deny(f"{path} is a large generated file. Use Grep with a precise pattern "
                 f"(e.g. IPHONEOS_DEPLOYMENT_TARGET, a target name, a string key), or Read with offset and limit.")
            return

    try:
        st = os.stat(path)
    except OSError:
        return
    mtime = int(st.st_mtime)

    if not ranged and st.st_size > LARGE_FILE_BYTES:
        try:
            with open(path, "rb") as f:
                lines = sum(1 for _ in f)
        except OSError:
            lines = 0
        deny(f"{path} is {st.st_size // 1024} KB ({lines} lines, roughly {st.st_size // 4:,} tokens). "
             f"Grep for the symbol you need, or Read with offset and limit on the relevant range. "
             f"Full reads of files over {LARGE_FILE_BYTES // 1024} KB are blocked to save context.")
        return

    sp = state_path(payload)
    state = load_state(sp)
    prev = state.get(path)
    if not ranged and prev and prev.get("mtime") == mtime and prev.get("full"):
        deny(f"{path} was already read in full this session and has not changed since "
             f"({time.strftime('%H:%M', time.localtime(prev['at']))}). Use the content already in context. "
             f"If it was lost to compaction, Read again with offset=1 and limit=2000, or Grep for the part you need.")
        return
    state[path] = {"mtime": mtime, "full": (not ranged) or bool(prev and prev.get("full")), "at": int(time.time())}
    save_state(sp, state)


if __name__ == "__main__":
    main()
