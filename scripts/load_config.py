#!/usr/bin/env python3
"""Load and validate the searching job configuration (config.json).

Usage as a module:
    from load_config import load_config, default_config_path
    cfg = load_config()            # ./config.json at the repository root
    cfg = load_config("my.json")   # explicit path

Usage as a script (prints the validated configuration as JSON):
    python3 scripts/load_config.py [--config PATH]

Exit codes: 0 = OK, 2 = configuration missing or invalid.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_KEYS = (
    "search_keywords",
    "location",
    "min_company_size",
    "max_company_size",
    "target_company_count",
    "backfill_company_keywords",
    "other_requirements",
)


class ConfigError(Exception):
    """Raised when config.json is missing or does not pass validation."""


def default_config_path() -> Path:
    return REPO_ROOT / "config.json"


def _nonneg_int(value: Any, name: str, *, allow_zero: bool = True) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{name} must be a non-negative number")
    n = int(value)
    if n < 0 or (not allow_zero and n < 1):
        raise ConfigError(f"{name} must be a non-negative number" if allow_zero else f"{name} must be at least 1")
    return n


def validate_config(data: Any) -> dict:
    if not isinstance(data, dict):
        raise ConfigError("config must be a JSON object")

    unknown = sorted(set(data) - set(ALLOWED_KEYS))
    if unknown:
        raise ConfigError(f"unknown config field(s): {', '.join(unknown)}")

    keywords = data.get("search_keywords")
    if not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
        raise ConfigError("search_keywords must be an array of strings")
    keywords = [k.strip() for k in keywords if k.strip()]
    if not keywords:
        raise ConfigError(
            "search_keywords is empty - add at least one job keyword to config.json "
            "before running (see README 'Initialisation')"
        )

    location = data.get("location", "")
    if not isinstance(location, str):
        raise ConfigError("location must be a string")

    min_size = _nonneg_int(data.get("min_company_size", 0), "min_company_size")
    max_size = _nonneg_int(data.get("max_company_size", 0), "max_company_size")
    if max_size and min_size and max_size < min_size:
        raise ConfigError("max_company_size must be >= min_company_size (or 0 to disable)")

    target = _nonneg_int(data.get("target_company_count", 5), "target_company_count", allow_zero=False)

    backfill = data.get("backfill_company_keywords", [])
    if backfill is None:
        backfill = []
    if not isinstance(backfill, list) or not all(isinstance(k, str) for k in backfill):
        raise ConfigError("backfill_company_keywords must be an array of strings")
    backfill = [k.strip() for k in backfill if k.strip()]

    other = data.get("other_requirements", "")
    if not isinstance(other, str):
        raise ConfigError("other_requirements must be a string")

    return {
        "search_keywords": keywords,
        "location": location.strip(),
        "min_company_size": min_size,
        "max_company_size": max_size,
        "target_company_count": target,
        "backfill_company_keywords": backfill,
        "other_requirements": other.strip(),
    }


def load_config(path: str | Path | None = None) -> dict:
    cfg_path = Path(path) if path else default_config_path()
    if not cfg_path.is_file():
        raise ConfigError(
            f"config not found: {cfg_path}\n"
            "Copy config.example.json to config.json and fill it in first."
        )
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config is not valid JSON ({cfg_path}): {exc}") from exc
    return validate_config(data)


def describe(cfg: dict) -> str:
    """Human-readable summary, handy for printing to stderr for the agent."""
    bf = ", ".join(cfg["backfill_company_keywords"]) or "(derive from search_keywords)"
    lines = [
        f"search_keywords: {', '.join(cfg['search_keywords'])}",
        f"location: {cfg['location'] or '(not set)'}",
        f"min_company_size: {cfg['min_company_size']}",
        f"max_company_size: {cfg['max_company_size'] or '(disabled)'}",
        f"target_company_count: {cfg['target_company_count']}",
        f"backfill_company_keywords: {bf}",
        f"other_requirements: {cfg['other_requirements'] or '(none)'}",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate and print config.json")
    ap.add_argument("--config", "-c", type=Path, help="Path to config.json")
    args = ap.parse_args()
    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"load_config error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(cfg, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
