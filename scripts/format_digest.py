#!/usr/bin/env python3
"""Render shortlist JSON to the exact digest format. Never hand-format the digest.

Per job: no numbering; three fields separated by a blank line.
Between companies: two Markdown rules ("---" newline "---").

Field 1: **Company** — Full official job title — [ad](url)
         OR (no-vacancy backfill): **Company** — <label> (no open ad) — none
Field 2: StreetNo StreetName StreetType, Suburb — headcount — [website](url)
         Address is simplified: Level/Suite/Unit/Floor and any building name
         before the street number are removed; state abbreviation and postcode
         are removed; "<City> CBD" becomes "<City>". Headcount like 1001~5000.
Field 3: Name — title — [LinkedIn](url) — email|none

Input fields per item: company, job_title, ad_url (or has_ad false / "none"),
website, street_address, suburb, headcount, lead_name, lead_title,
lead_linkedin (optional), lead_email (optional).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FLOOR_PREFIX = re.compile(
    r"^(?:(?:levels?|lvl|l)\s*[\d&\-– ]+|suite\s*\w+|unit\s*\w+|shop\s*\w+|"
    r"(?:ground|\d+(?:st|nd|rd|th))\s+floor|floor\s*\d+)\s*[,/]?\s*",
    re.I,
)
STATES = r"(?:VIC|NSW|QLD|SA|WA|TAS|NT|ACT)"
STATE_POSTCODE_TAIL = re.compile(rf"(?:[\s,]+{STATES})?(?:[\s,]+\d{{4}})?\s*$", re.I)
STATE_WORD = re.compile(rf"\b{STATES}\b")
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
CBD = re.compile(r"^\s*(.+?)\s+CBD\s*$", re.I)

SEPARATOR = "\n\n---\n---\n\n"


def die(msg: str) -> None:
    print(f"format_digest error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def has_open_ad(item: dict) -> bool:
    if item.get("has_ad") is False:
        return False
    ad = str(item.get("ad_url") or "").strip().lower()
    if ad in ("", "none", "n/a", "na"):
        return False
    return True


def simplify_address(street: str, suburb: str) -> str:
    street = EMAIL.sub("", (street or "")).strip().strip(",")
    suburb = EMAIL.sub("", (suburb or "")).strip().strip(",")

    while True:
        nxt = FLOOR_PREFIX.sub("", street).strip()
        if nxt == street:
            break
        street = nxt

    m = re.search(r"(?:^|,\s*)(\d+[A-Za-z]?(?:[-–]\d+[A-Za-z]?)?\s+[^,]+)", street)
    if m:
        street = m.group(1).strip()

    street = street.split(",")[0].strip()
    street = STATE_POSTCODE_TAIL.sub("", street).strip(" ,")

    suburb = STATE_POSTCODE_TAIL.sub("", suburb).strip(" ,")
    suburb = STATE_WORD.sub("", suburb).strip(" ,")
    cbd = CBD.match(suburb)
    if cbd:
        suburb = cbd.group(1).strip()

    if not street or not suburb:
        die("street_address and suburb are required (after simplification)")
    return f"{street}, {suburb}"


def normalise_headcount(hc: str) -> str:
    hc = str(hc or "").strip()
    if not hc:
        die("headcount missing")
    nums = [n.replace(",", "") for n in re.findall(r"\d[\d,]*", hc)]
    if len(nums) >= 2:
        return f"{nums[0]}~{nums[1]}"
    if len(nums) == 1:
        return f"{nums[0]}+" if "+" in hc else nums[0]
    return hc


def render_item(item: dict) -> str:
    company = str(item.get("company") or "").strip()
    title = str(item.get("job_title") or "").strip()
    ad = str(item.get("ad_url") or "").strip()
    web = str(item.get("website") or "").strip()
    if not company or not title:
        die("company and job_title required")
    if not web.startswith("http"):
        die(f"{company}: website must be an http(s) URL")

    open_ad = has_open_ad(item)
    if open_ad:
        if not ad.startswith("http"):
            die(f"{company}: ad_url must be an http(s) URL when has_ad")
    else:
        if title.strip().lower() in ("", "none"):
            title = "Company outreach (no open ad)"

    addr = simplify_address(item.get("street_address") or "", item.get("suburb") or "")
    headcount = normalise_headcount(item.get("headcount") or "")

    lead_name = str(item.get("lead_name") or "").strip()
    lead_title = str(item.get("lead_title") or "").strip()
    lead_li = str(item.get("lead_linkedin") or "").strip()
    if not lead_name or not lead_title:
        die(f"{company}: lead_name and lead_title required")
    email = item.get("lead_email")
    email_out = "none" if email is None or str(email).strip().lower() in ("", "none") else str(email).strip()
    li_out = f"[LinkedIn]({lead_li})" if lead_li.startswith("http") else "none"

    if open_ad:
        field1 = f"**{company}** — {title} — [ad]({ad})"
    else:
        field1 = f"**{company}** — {title} — none"
    field2 = f"{addr} — {headcount} — [website]({web})"
    field3 = f"{lead_name} — {lead_title} — {li_out} — {email_out}"
    return "\n\n".join([field1, field2, field3])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", "-i", type=Path, help="Shortlist JSON array (default: stdin)")
    ap.add_argument("--output", "-o", type=Path, help="Also write the digest to this file")
    args = ap.parse_args()
    raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    items = json.loads(raw)
    if not isinstance(items, list) or not items:
        die("expected a non-empty JSON array")
    digest = SEPARATOR.join(render_item(item) for item in items) + "\n"
    if args.output:
        args.output.write_text(digest, encoding="utf-8")
    sys.stdout.write(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
