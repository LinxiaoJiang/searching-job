---
name: searching job
description: >-
  Build a job-outreach shortlist for any field. The user configures search
  keywords, location, minimum company size and other requirements in
  config.json; jobs are researched logged out on SEEK, Indeed and LinkedIn
  Jobs; the digest is rendered and validated only by the bundled scripts.
---
# searching job

A general job-outreach shortlist. For each suitable job ad, find the company, its office address and headcount, and one relevant person to contact. Output a fixed-format digest. Never send outreach (email, LinkedIn message, application) unless the user explicitly asks.

## Configuration (required before first run)

Read `config.json` at the repository root (copied from `config.example.json`):

| Field | Type | Meaning |
|---|---|---|
| `search_keywords` | string array | Job keywords to search. **Required.** If empty or missing, stop and ask the user to configure it. |
| `location` | string | City / region to search, e.g. `Melbourne VIC`. |
| `min_company_size` | number | Minimum company headcount (lower bound of the LinkedIn band). `0` disables the check. |
| `other_requirements` | string | Free-text rules to apply during research (e.g. "office-based only", "no roles requiring citizenship"). |

Check it with: `python3 scripts/load_config.py` (exit code 2 = not configured).

## Job boards (fixed)

Search **logged out** only:

- SEEK — https://www.seek.com.au
- Indeed — https://au.indeed.com
- LinkedIn Jobs — https://www.linkedin.com/jobs

Do not log in, and do not bypass captchas or bot checks. If a board blocks access, note it and continue with the others.

## Research rules

- Use every keyword in `search_keywords` against `location`.
- Apply `other_requirements` yourself when reading each ad; drop ads that clearly conflict with them.
- Record the **full official job title** as written in the ad and the direct ad URL.
- Company website, office street address, suburb and headcount must come from a real source (company site, LinkedIn company page, the ad). Headcount: use the LinkedIn band, e.g. `1,001-5,000`.
- Contact: one relevant person (hiring manager, team lead, talent acquisition). LinkedIn URL if found; email only if publicly listed, otherwise `none`.
- **Never invent** names, titles, addresses, URLs, emails or headcounts. If something cannot be verified, leave it empty and drop or flag the job.

## Pipeline

```bash
python3 scripts/filter_candidates.py -i candidates.json --rejected rejected.json > kept.json
python3 scripts/format_digest.py -i kept.json -o digest.md
python3 scripts/validate_digest.py digest.md
```

`filter_candidates.py` checks required fields (`company`, `job_title`, `ad_url`, `website`) and `min_company_size`, and prints the active keywords, location and other requirements to stderr. Only paste the digest after `validate_digest.py` prints `OK`. Never hand-format the digest.

### Candidate JSON fields

`company`, `job_title`, `ad_url`, `website`, `street_address`, `suburb`, `headcount`, `lead_name`, `lead_title`, `lead_linkedin` (optional), `lead_email` (optional).

## Digest format (code-enforced)

- No numbering.
- Three fields per job, with a blank line between fields.
- Between companies: two Markdown rules (`---` on one line, `---` on the next).

1. `**Company** — Full official job title — [ad](url)`
2. `StreetNo StreetName StreetType, Suburb — headcount — [website](url)`
3. `Name — title — [LinkedIn](url) — email|none`

Address simplification is automatic: Level/Suite/Unit/Floor and any building name before the street number are removed, state and postcode are removed, and `<City> CBD` becomes `<City>`.
