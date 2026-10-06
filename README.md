# searching job

[简体中文](README.zh-CN.md)

**searching job** is an agent skill that builds a job-outreach shortlist for any field. You tell it what jobs to look for, where, and what else matters to you; an AI agent researches job ads on SEEK, Indeed and LinkedIn Jobs (logged out), finds each company's office address, headcount and a relevant contact person, and produces a tidy, fixed-format digest.

The digest is always rendered and checked by the bundled Python scripts, so the format never drifts. The skill never sends emails, messages or applications on your behalf.

## Licence

Released under the [MIT Licence](LICENSE).

## Prerequisites

- Python 3.8 or later (no third-party packages needed)
- An AI agent or assistant that can read `SKILL.md` and browse the web (for the research step)
- Git (optional - you can download the release zip instead)

## What's in the repository

```
searching-job/
├── SKILL.md                    # Instructions for the agent
├── config.example.json         # Configuration template - copy to config.json
├── scripts/
│   ├── load_config.py          # Loads and validates config.json
│   ├── filter_candidates.py    # Required fields + minimum company size
│   ├── format_digest.py        # Renders the digest
│   └── validate_digest.py      # Checks the digest format
├── examples/
│   └── sample_candidates.json  # Fake data for trying the pipeline
├── README.md / README.zh-CN.md
└── LICENSE
```

## Initialisation (step by step)

### 1. Get the files

Either clone the repository:

```bash
git clone https://github.com/LinxiaoJiang/searching-job.git
cd searching-job
```

or download `searching-job-vX.Y.Z.zip` from the **Releases** page, unzip it, and open the folder in a terminal.

If your agent loads skills from a particular folder, copy (or symlink) the whole `searching-job` folder there.

### 2. Create your configuration file

```bash
cp config.example.json config.json
```

On Windows (PowerShell): `Copy-Item config.example.json config.json`

`config.json` is listed in `.gitignore`, so your personal settings are never committed.

### 3. Fill in `config.json`

```json
{
  "search_keywords": ["graduate data analyst", "junior business analyst"],
  "location": "Melbourne VIC",
  "min_company_size": 100,
  "other_requirements": "Office-based or hybrid roles only. Skip ads that require security clearance."
}
```

| Field | Required | What to put in it |
|---|---|---|
| `search_keywords` | **Yes** | One or more job keywords, as you would type them into SEEK. If this list is empty, the scripts refuse to run. |
| `location` | Recommended | City or region to search, e.g. `Melbourne VIC`, `Sydney NSW`, `Brisbane`. |
| `min_company_size` | Recommended | Minimum company headcount (compared with the lower bound of the LinkedIn band, e.g. `201-500` counts as 201). Use `0` to turn the check off. |
| `other_requirements` | Optional | Any other rules, in plain words. The agent applies these while reading each ad (e.g. role type, visa or citizenship conditions, industries to avoid, work arrangements). |

Check your configuration:

```bash
python3 scripts/load_config.py
```

It prints the validated settings, or an error (exit code 2) explaining what to fix.

### 4. Run the pipeline

Ask your agent to follow `SKILL.md` (for example: "Run the searching job skill"). It researches ads and saves what it finds as a JSON array, e.g. `candidates.json`. Then:

```bash
# 1) Keep candidates that have the required fields and meet min_company_size
python3 scripts/filter_candidates.py -i candidates.json --rejected rejected.json > kept.json

# 2) Render the digest
python3 scripts/format_digest.py -i kept.json -o digest.md

# 3) Validate the digest - only use it if this prints "validate_digest OK"
python3 scripts/validate_digest.py digest.md
```

`load_config.py` and `filter_candidates.py` accept `--config path/to/config.json`; every script reads from stdin when `-i` is omitted.

Try it straight away with the bundled fake data:

```bash
python3 scripts/filter_candidates.py -i examples/sample_candidates.json > /tmp/kept.json
python3 scripts/format_digest.py -i /tmp/kept.json -o /tmp/digest.md
python3 scripts/validate_digest.py /tmp/digest.md
```

### Candidate JSON fields

| Field | Notes |
|---|---|
| `company` | Company name |
| `job_title` | Full official job title from the ad |
| `ad_url` | Direct link to the job ad |
| `website` | Company website |
| `street_address` | e.g. `Level 12, 100 Sample Street` (simplified automatically) |
| `suburb` | e.g. `Melbourne CBD VIC 3000` (simplified automatically) |
| `headcount` | LinkedIn band, e.g. `1,001-5,000` |
| `lead_name`, `lead_title` | One relevant contact person |
| `lead_linkedin` | Optional LinkedIn profile URL |
| `lead_email` | Optional; only if publicly listed - otherwise empty or `none` |

## Job boards

Searches are done **logged out** on:

- [SEEK](https://www.seek.com.au)
- [Indeed](https://au.indeed.com)
- [LinkedIn Jobs](https://www.linkedin.com/jobs)

The agent does not log in and does not bypass captchas or bot checks.

## Digest format

- No numbering.
- Three fields per job, separated by a blank line.
- Between companies: two Markdown rules (`---` then `---`).

```
**Company** — Full official job title — [ad](url)

StreetNo StreetName StreetType, Suburb — headcount — [website](url)

Name — title — [LinkedIn](url) — email|none

---
---

**Next Company** — ...
```

Addresses are simplified automatically: Level/Suite/Unit/Floor and building names before the street number are removed, state and postcode are removed, and `Melbourne CBD` becomes `Melbourne`. Headcount bands are shown as `1001~5000`.

## Releases and the install zip

Each tagged version (e.g. `v0.1.0`) has a GitHub Release with:

- `searching-job-vX.Y.Z.zip` - a ready-to-use package (`SKILL.md`, `scripts/`, `examples/`, `config.example.json`, READMEs, licence)
- the source code archives GitHub generates automatically

To install from a release: download the zip, unzip it, then follow **Initialisation** from step 2.

Maintainers can build the zip with:

```bash
git archive --format=zip --prefix=searching-job/ -o searching-job-v0.1.0.zip v0.1.0
```

## Ground rules

- Nothing is invented: unverifiable details are left out, not guessed.
- No outreach is sent unless you explicitly ask for it.
- The digest is only ever produced by `format_digest.py` and checked by `validate_digest.py`.
