---
name: searching job
description: >-
  Build a job-outreach shortlist for any field. The user configures search
  keywords, location, company size band, target count and other requirements in
  config.json; jobs are researched logged out on SEEK, Indeed and LinkedIn
  Jobs; fill to target_company_count (ads first, then related companies without
  vacancies); the digest is rendered and validated only by the bundled scripts.
---
# searching job

A general job-outreach shortlist. For each suitable company (with or without a live ad), find the office address and headcount, and one relevant person to contact. Output a fixed-format digest. Never send outreach (email, LinkedIn message, application) unless the user explicitly asks.

## Configuration (required before first run)

Read `config.json` at the repository root (copied from `config.example.json`):

| Field | Type | Meaning |
|---|---|---|
| `search_keywords` | string array | Job keywords to search. **Required.** If empty or missing, stop and ask the user to configure it. |
| `location` | string | City / region to search, e.g. `Melbourne VIC`. |
| `min_company_size` | number | Minimum company headcount (lower bound of the LinkedIn band). `0` disables the check. |
| `max_company_size` | number | Maximum company headcount (upper bound of the LinkedIn band). `0` disables the check. |
| `target_company_count` | number | How many companies to aim for each run (default `5`). |
| `backfill_company_keywords` | string array | Keywords for finding **companies** (not job ads) when ads alone are fewer than the target. If empty, derive sensible company-search terms from `search_keywords` (e.g. drop "graduate" / "junior" and keep the field). |
| `other_requirements` | string | Free-text rules to apply during research (e.g. "office-based only", "no roles requiring citizenship"). |

Check it with: `python3 scripts/load_config.py` (exit code 2 = not configured).

## Target count (fill to N)

Each run aims for **`target_company_count` companies** (default 5). Deliver fewer only if fewer firms pass every hard filter.

1. **Ads first.** Search SEEK / Indeed / LinkedIn Jobs (logged out) using every `search_keywords` entry against `location`. Keep companies that pass size / `other_requirements` and have a live job ad.
2. **If ads ≥ target:** take the best `target_company_count` with ads. Do **not** add companies that have no open vacancy.
3. **If ads are 1..(target−1):** keep all qualifying ad companies, then **backfill** the remainder by searching for companies matching `backfill_company_keywords` (or derived terms) in `location`, even if they have **no current vacancy**.
4. **If ads are 0:** search and list up to `target_company_count` such related companies (no vacancy required), still under size and `other_requirements`.

List companies with ads ahead of no-ad backfills. Prefer distinct companies (one entry per company).

## Job boards (fixed)

Search **logged out** only:

- SEEK — https://www.seek.com.au
- Indeed — https://au.indeed.com
- LinkedIn Jobs — https://www.linkedin.com/jobs

Do not log in, and do not bypass captchas or bot checks. If a board blocks access, note it and continue with the others.

## Research rules

- Use every keyword in `search_keywords` against `location`.
- Apply `other_requirements` yourself when reading each ad or company profile; drop anything that clearly conflicts.
- For ads: record the **full official job title** as written and the direct ad URL.
- For no-ad backfill: set `has_ad` to `false` (or `ad_url` to `none`) and use a clear title such as `Company outreach (no open ad)` — never invent a fake ad URL.
- Company website, office street address, suburb and headcount must come from a real source (company site, LinkedIn company page, the ad). Headcount: use the LinkedIn band, e.g. `1,001-5,000`.
- Contact: one relevant person (hiring manager, team lead, talent acquisition). LinkedIn URL if found; email only if publicly listed, otherwise `none`.
- **Never invent** names, titles, addresses, URLs, emails or headcounts. If something cannot be verified, leave it empty and drop or flag the entry.

## Pipeline

```bash
python3 scripts/filter_candidates.py -i candidates.json --rejected rejected.json > kept.json
python3 scripts/format_digest.py -i kept.json -o digest.md
python3 scripts/validate_digest.py digest.md
```

`filter_candidates.py` checks required fields, `min_company_size` / `max_company_size`, and prints the active config (including target and backfill keywords) to stderr. Only paste the digest after `validate_digest.py` prints `OK`. Never hand-format the digest.

### Candidate JSON fields

`company`, `job_title`, `ad_url` (http URL, or omit / `"none"` / `has_ad: false` for backfill), `website`, `street_address`, `suburb`, `headcount`, `lead_name`, `lead_title`, `lead_linkedin` (optional), `lead_email` (optional), `has_ad` (optional bool).

## Digest format (code-enforced)

- No numbering.
- Three fields per job, with a blank line between fields.
- Between companies: two Markdown rules (`---` on one line, `---` on the next).

**With an open ad:**

1. `**Company** — Full official job title — [ad](url)`
2. `StreetNo StreetName StreetType, Suburb — headcount — [website](url)`
3. `Name — title — [LinkedIn](url) — email|none`

**Without an open vacancy (backfill only):**

1. `**Company** — Company outreach (no open ad) — none`
2. Same address / headcount / website line
3. Same contact line

Address simplification is automatic: Level/Suite/Unit/Floor and any building name before the street number are removed, state and postcode are removed, and `<City> CBD` becomes `<City>`.
