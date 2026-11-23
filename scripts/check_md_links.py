#!/usr/bin/env python3
"""Fail if a published (git-tracked) markdown file links to a file that is not
itself tracked — i.e. a link that would 404 on GitHub.

Internal docs are intentionally kept out of the repo (see .gitignore), so a
tracked doc must never link to one. Run from the repo root:

    python3 scripts/check_md_links.py

Exit 0 = clean, 1 = broken links.
"""
import os
import re
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LINK = re.compile(r"(\[[^\]]*\]\()([^)\s#][^)]*?)(\))")
SKIP = ("http://", "https://", "mailto:", "tel:", "#")


def tracked_files():
    out = subprocess.check_output(["git", "-C", ROOT, "ls-files"], text=True)
    return {line for line in out.splitlines() if line}


def main():
    tracked = tracked_files()
    tracked_md = sorted(f for f in tracked if f.endswith(".md"))
    broken = defaultdict(list)

    for rel in tracked_md:
        base = os.path.dirname(os.path.join(ROOT, rel))
        for m in LINK.finditer(open(os.path.join(ROOT, rel)).read()):
            target = m.group(2).split(" ")[0].split("#")[0]
            if not target or target.startswith(SKIP):
                continue
            resolved = os.path.relpath(os.path.normpath(os.path.join(base, target)), ROOT)
            if resolved not in tracked:
                broken[rel].append(target)

    if broken:
        print("BROKEN LINKS (target not published in the repo):")
        for f, targets in sorted(broken.items()):
            joined = ", ".join(sorted(targets))
            print(f"  {f} -> {joined}")
        return 1
    print(f"All links in {len(tracked_md)} published markdown files resolve to tracked files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
