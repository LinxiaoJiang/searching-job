#!/usr/bin/env python3
"""Filter shortlist candidates against config.json.

Reads a JSON array of candidates from --input or stdin and writes the kept
candidates to stdout as JSON.

Mechanical checks applied here:
  * required fields present: company, job_title, ad_url, website
  * company headcount >= min_company_size (lower bound of a band such as
    "1,001-5,000"; candidates with no headcount are kept and flagged)

Everything else - matching search_keywords and location, and honouring the
free-text other_requirements - is the agent's job during research. This
script prints those settings to stderr so the agent keeps them in view.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_config import ConfigError, describe, load_config  # noqa: E402

REQUIRED_FIELDS = ("company", "job_title", "ad_url", "website")


def parse_min_headcount(headcount: str | None) -> int | None:
    if not headcount:
        return None
    nums = [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", str(headcount))]
    return min(nums) if nums else None


def reason_reject(item: dict, min_size: int) -> str | None:
    for field in REQUIRED_FIELDS:
        if not str(item.get(field) or "").strip():
            return f"missing_{field}"
    hc = parse_min_headcount(item.get("headcount"))
    if min_size and hc is not None and hc < min_size:
        return f"company_size_under_{min_size}"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", "-i", type=Path, help="Candidates JSON array (default: stdin)")
    ap.add_argument("--config", "-c", type=Path, help="Path to config.json (default: repo root)")
    ap.add_argument("--rejected", type=Path, help="Write rejected [{reason, item}] JSON here")
    args = ap.parse_args()

    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"filter_candidates error: {exc}", file=sys.stderr)
        return 2

    raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    try:
        candidates = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"filter_candidates error: input is not valid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(candidates, list):
        print("filter_candidates error: input must be a JSON array", file=sys.stderr)
        return 2

    min_size = cfg["min_company_size"]
    kept, rejected, no_headcount = [], [], []
    for item in candidates:
        if not isinstance(item, dict):
            rejected.append({"reason": "not_an_object", "item": item})
            continue
        why = reason_reject(item, min_size)
        if why:
            rejected.append({"reason": why, "item": item})
        else:
            kept.append(item)
            if parse_min_headcount(item.get("headcount")) is None:
                no_headcount.append(item.get("company"))

    if args.rejected:
        args.rejected.write_text(json.dumps(rejected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(kept, ensure_ascii=False, indent=2))

    print("# config in force (agent: apply keywords, location and other_requirements during research)", file=sys.stderr)
    for line in describe(cfg).splitlines():
        print(f"#   {line}", file=sys.stderr)
    if no_headcount:
        print(f"# warning: no headcount for: {', '.join(map(str, no_headcount))} (verify before formatting)", file=sys.stderr)
    for r in rejected:
        name = r["item"].get("company") if isinstance(r["item"], dict) else r["item"]
        print(f"# rejected: {name} ({r['reason']})", file=sys.stderr)
    print(f"# kept={len(kept)} rejected={len(rejected)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
