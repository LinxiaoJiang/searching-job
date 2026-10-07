# searching job

[简体中文](README.zh-CN.md)

Agent skill for a job-outreach shortlist. Configure keywords and filters; the agent searches SEEK, Indeed and LinkedIn Jobs **logged out**, finds company address / headcount / a contact, and emits a fixed-format digest via the bundled scripts. Never sends outreach unless you ask.

MIT — see [LICENSE](LICENSE).

## Setup

```bash
git clone https://github.com/LinxiaoJiang/searching-job.git
cd searching-job
cp config.example.json config.json
```

Or download the zip from [Releases](https://github.com/LinxiaoJiang/searching-job/releases).

Edit `config.json`, then check it:

```bash
python3 scripts/load_config.py
```

| Field | Notes |
|---|---|
| `search_keywords` | **Required.** Job search terms (SEEK-style). |
| `location` | e.g. `Melbourne VIC`. |
| `min_company_size` / `max_company_size` | LinkedIn headcount band bounds; `0` = off. |
| `target_company_count` | Aim for this many companies each run (default `5`). |
| `backfill_company_keywords` | Company search terms when ads are short of the target; empty → derive from `search_keywords`. |
| `other_requirements` | Free-text rules the agent applies while researching. |

## Fill to target

Aim for `target_company_count` companies:

1. Prefer firms with a live matching ad.
2. If ads ≥ target → stop (no no-vacancy backfill).
3. If ads < target → keep ads, backfill related companies (even with no open role).
4. If ads = 0 → list up to the target of related companies only.

## Pipeline

```bash
python3 scripts/filter_candidates.py -i candidates.json --rejected rejected.json > kept.json
python3 scripts/format_digest.py -i kept.json -o digest.md
python3 scripts/validate_digest.py digest.md
```

Paste the digest only after `validate_digest OK`. Never hand-format.

Try the sample (set `search_keywords` in a temp config first):

```bash
python3 scripts/filter_candidates.py -i examples/sample_candidates.json --config /path/to/config.json > /tmp/kept.json
python3 scripts/format_digest.py -i /tmp/kept.json -o /tmp/digest.md
python3 scripts/validate_digest.py /tmp/digest.md
```

### Candidate fields

`company`, `job_title`, `ad_url` (or `none` / `has_ad: false` for backfill), `website`, `street_address`, `suburb`, `headcount`, `lead_name`, `lead_title`, optional `lead_linkedin` / `lead_email`.

## Digest

No numbering. Three fields per company; blank line between fields; `---` then `---` between companies.

```
**Company** — Full job title — [ad](url)

Street, Suburb — headcount — [website](url)

Name — title — [LinkedIn](url) — email|none
```

No vacancy: `**Company** — Company outreach (no open ad) — none`. Addresses drop Level/Suite/state/postcode; CBD → city name; headcount like `1001~5000`.

## Layout

```
SKILL.md · config.example.json · scripts/ · examples/ · README*.md · LICENSE
```

Python 3.8+, no third-party packages. Job boards: SEEK, Indeed, LinkedIn Jobs — logged out only; no captcha bypass.
