#!/usr/bin/env python3
"""Validate a digest: unnumbered jobs, three fields each, blank lines between
fields, and a double Markdown rule ("---" / "---") between companies."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

F1 = re.compile(r"^\*\*[^*]+\*\* — .+ — (?:\[ad\]\(https?://[^)\s]+\)|none)$")
F2 = re.compile(r"^[^—]+, [^—]+ — [^—]+ — \[website\]\(https?://[^)\s]+\)$")
F3 = re.compile(r"^[^—]+ — [^—]+ — (?:\[LinkedIn\]\(https?://[^)\s]+\)|none) — (?:[\w.+-]+@[\w.-]+\.\w+|none)$")
NUMBERED = re.compile(r"^\s*(?:\d+[.)]|#\d+)\s")
FLOOR = re.compile(r"\b(?:Level|Lvl|Suite|Unit|Floor)\b", re.I)
STATE_POSTCODE = re.compile(r"\b(?:VIC|NSW|QLD|SA|WA|TAS|NT|ACT)\b|\b\d{4}$")


def split_blocks(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").strip("\n")
    return [b for b in re.split(r"\n\n---\n---\n\n", text)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=Path, nargs="?", help="Digest file (default: stdin)")
    args = ap.parse_args()
    text = args.path.read_text(encoding="utf-8") if args.path else sys.stdin.read()
    if not text.strip():
        print("validate_digest FAILED: empty digest", file=sys.stderr)
        return 1

    errors: list[str] = []
    blocks = split_blocks(text)
    for idx, block in enumerate(blocks, 1):
        lines = block.split("\n")
        if len(lines) != 5 or lines[1] != "" or lines[3] != "":
            errors.append(
                f"job {idx}: expected 3 fields separated by single blank lines, "
                "and '---' then '---' between companies"
            )
            continue
        f1, f2, f3 = lines[0], lines[2], lines[4]
        for f in (f1, f2, f3):
            if NUMBERED.match(f):
                errors.append(f"job {idx}: numbering is not allowed")
        if not F1.match(f1):
            errors.append(
                f"job {idx} field 1: expected '**Company** — Title — [ad](url)' "
                "or '**Company** — Title — none'"
            )
        if not F2.match(f2):
            errors.append(f"job {idx} field 2: expected 'Street, Suburb — headcount — [website](url)'")
        else:
            addr = f2.split(" — ")[0]
            if FLOOR.search(addr):
                errors.append(f"job {idx} field 2: remove Level/Suite/Unit/Floor from the address")
            if STATE_POSTCODE.search(addr):
                errors.append(f"job {idx} field 2: remove state and postcode from the address")
        if not F3.match(f3):
            errors.append(f"job {idx} field 3: expected 'Name — title — [LinkedIn](url)|none — email|none'")

    if errors:
        print("validate_digest FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"validate_digest OK: {len(blocks)} jobs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
