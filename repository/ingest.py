"""
FanVerse Research Repository — Ingestion Engine
------------------------------------------------
Handles:
  - Writing records to the .jsonl repository file
  - Deduplication: skips any record whose record_id already exists
  - Merge-safe: safe to re-run on a schedule, no duplicate records added
  - Logging: prints a summary after every run
"""

import json
import os
from datetime import datetime
from pathlib import Path
from schema import build_record

REPO_PATH = Path("repository.jsonl")
LOG_PATH = Path("ingestion_log.jsonl")


# ── Core I/O ──────────────────────────────────────────────────────────────────

def load_existing_ids() -> set[str]:
    """Load all record_ids already in the repository."""
    if not REPO_PATH.exists():
        return set()
    ids = set()
    with open(REPO_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    ids.add(json.loads(line)["record_id"])
                except (json.JSONDecodeError, KeyError):
                    pass
    return ids


def append_records(records: list[dict]) -> dict:
    """
    Append new records to repository.jsonl, skipping duplicates.
    Returns a summary: {added, skipped, total_in_repo}
    """
    existing_ids = load_existing_ids()
    added = 0
    skipped = 0

    with open(REPO_PATH, "a") as f:
        for record in records:
            if record["record_id"] in existing_ids:
                skipped += 1
                continue
            f.write(json.dumps(record) + "\n")
            existing_ids.add(record["record_id"])
            added += 1

    total = len(existing_ids)
    summary = {
        "run_at": datetime.utcnow().isoformat() + "Z",
        "added": added,
        "skipped_duplicates": skipped,
        "total_in_repo": total,
    }

    # Append to log
    with open(LOG_PATH, "a") as log:
        log.write(json.dumps(summary) + "\n")

    print(f"[Ingestion] ✓ {added} added  |  {skipped} skipped (duplicates)  |  {total} total in repo")
    return summary


# ── Query helpers ─────────────────────────────────────────────────────────────

def load_all() -> list[dict]:
    """Load every record from the repository into memory."""
    if not REPO_PATH.exists():
        return []
    records = []
    with open(REPO_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def query(source=None, sport=None, season_phase=None) -> list[dict]:
    """Simple filter query. All args optional — pass what you want to filter by."""
    records = load_all()
    if source:
        records = [r for r in records if r["source"] == source.lower()]
    if sport:
        records = [r for r in records if sport in r.get("sports", [])]
    if season_phase:
        records = [r for r in records if r.get("season_phase") == season_phase]
    return records


def repo_stats() -> dict:
    """Print a summary of what's currently in the repository."""
    records = load_all()
    if not records:
        print("[Repo] Empty.")
        return {}

    from collections import Counter
    sources = Counter(r["source"] for r in records)
    sports = Counter(s for r in records for s in r.get("sports", []))
    phases = Counter(r.get("season_phase", "unknown") for r in records)

    stats = {
        "total_records": len(records),
        "by_source": dict(sources),
        "by_sport": dict(sports),
        "by_season_phase": dict(phases),
    }
    print(json.dumps(stats, indent=2))
    return stats


# ── Ingestion runner ──────────────────────────────────────────────────────────

def ingest(raw_entries: list[dict]) -> dict:
    """
    Main entry point. Pass a list of dicts with the fields needed by build_record().
    Example entry:
        {
            "text": "72% of female WNBA fans say...",
            "source": "nielsen",
            "report_title": "Nielsen Fan Insights 2024",
            "url": "https://...",
            "sports": ["WNBA"],
            "date": "2024-03-01",
            "season_phase": "preseason"
        }
    """
    records = [build_record(**entry) for entry in raw_entries]
    return append_records(records)