#!/usr/bin/env python3
"""Manual reindex: python3 reindex.py [project-root]. Prints a one-line summary."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sco_common as sco  # noqa: E402

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
entries = sco.build_index(root)
path = sco.write_index(root, entries)
print(f"Indexed {len(entries)} components into {path.relative_to(root)}")
