#!/usr/bin/env python3
"""Reads xcodebuild / swift build / swift test output on stdin, prints only what
matters: errors, warnings (deduplicated), failing tests, test totals and the verdict.
Preserves the upstream exit code via pipefail in the calling shell."""
import re
import sys

KEEP = re.compile(
    r"(: error:|: warning:|error: |fatal error|\*\* (BUILD|TEST|ARCHIVE|CLEAN) (SUCCEEDED|FAILED|INTERRUPTED)|"
    r"Test Suite .* (passed|failed)|Test Case .* failed|Executed \d+ tests?|XCTAssert|"
    r"error: .*failed|Compiling failed|The following build commands failed|"
    r"Testing failed|Testing started|Build complete!|\[\d+/\d+\] .*error|"
    r"Undefined symbols|ld: |linker command failed|Could not find|No such module|"
    r"xcodebuild: error|Command .* failed with a nonzero exit code|Fatal error)",
    re.I,
)
MAX_LINES = 150


def main():
    seen = set()
    kept = []
    total = 0
    for raw in sys.stdin:
        total += 1
        line = raw.rstrip("\n")
        if not KEEP.search(line):
            continue
        key = re.sub(r"\s+", " ", line.strip())
        if key in seen:
            continue
        seen.add(key)
        kept.append(line.strip()[:400])
    if not kept:
        print(f"[build filter] no errors or warnings in {total} lines of output")
        return
    shown = kept[:MAX_LINES]
    print("\n".join(shown))
    hidden = len(kept) - len(shown)
    tail = f", {hidden} more matching lines hidden" if hidden else ""
    print(f"[build filter] {len(kept)} relevant lines from {total} total{tail}")


if __name__ == "__main__":
    main()
