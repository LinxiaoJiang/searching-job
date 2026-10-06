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
ALLOWED_KEYS = ("search_keywords", "location", "min_company_size", "other_requirements")


class ConfigError(Exception):
    """Raised when config.json is missing or does not pass validation."""


def default_config_path() -> Path:
    return REPO_ROOT / "config.json"


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

    min_size = data.get("min_company_size", 0)
    if isinstance(min_size, bool) or not isinstance(min_size, (int, float)) or min_size < 0:
        raise ConfigError("min_company_size must be a non-negative number (0 disables the check)")

    other = data.get("other_requirements", "")
    if not isinstance(other, str):
        raise ConfigError("other_requirements must be a string")

    return {
        "search_keywords": keywords,
        "location": location.strip(),
        "min_company_size": int(min_size),
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
    lines = [
        f"search_keywords: {', '.join(cfg['search_keywords'])}",
        f"location: {cfg['location'] or '(not set)'}",
        f"min_company_size: {cfg['min_company_size']}",
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
