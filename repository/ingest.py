# ingest.py
# Handles saving records to the repository file and reading them back out.
# The main thing it does: never save the same record twice.

import json
from datetime import datetime
from pathlib import Path
from schema import build_record

REPO_PATH = Path("repository.jsonl")    # the main data file — one record per line
LOG_PATH = Path("ingestion_log.jsonl")  # keeps a log of every time the ingestion ran

def load_existing_ids() -> set[str]:
    # Reads the repository and returns all the record fingerprints already saved.
    # Used to check for duplicates before writing anything new.
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
                    pass  # skip any corrupted lines
    return ids

def load_all() -> list[dict]:
    # Loads every record from the repository into memory.
    # Used by the query and stats functions below.
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

def append_records(records: list[dict]) -> dict:
    # Saves new records to the repository, skipping any that already exist.
    # Safe to run on a schedule. It only ever adds new lines, never overwrites.
    existing_ids = load_existing_ids()
    added = 0
    skipped = 0

    with open(REPO_PATH, "a") as f:  # "a" = append mode, never overwrites
        for record in records:
            if record["record_id"] in existing_ids:
                skipped += 1
                continue
            f.write(json.dumps(record) + "\n")
            existing_ids.add(record["record_id"])
            added += 1

    total = len(existing_ids)

    # Save a summary of this run to the log
    summary = {
        "run_at": datetime.utcnow().isoformat() + "Z",
        "added": added,
        "skipped_duplicates": skipped,
        "total_in_repo": total,
    }
    with open(LOG_PATH, "a") as log:
        log.write(json.dumps(summary) + "\n")

    print(f"[Ingestion] + {added} added  |  {skipped} skipped (duplicates)  |  {total} total in repo")
    return summary

def query(source=None, sport=None, season_phase=None) -> list[dict]:
    # Filters the repository by source, sport, or season phase.
    # All arguments are optional — pass only what you want to filter by.
    # Example: query(source="nielsen", sport="NBA")
    records = load_all()

    if source:
        records = [r for r in records if r["source"] == source.lower()]
    if sport:
        records = [r for r in records if sport in r.get("sports", [])]
    if season_phase:
        records = [r for r in records if r.get("season_phase") == season_phase]

    return records


def repo_stats() -> dict:
    # Prints a breakdown of everything in the repository.
    # Good for a quick health check - total records, broken down by source/sport/phase.
    records = load_all()

    if not records:
        print("[Repo] Empty.")
        return {}

    from collections import Counter
    stats = {
        "total_records": len(records),
        "by_source": dict(Counter(r["source"] for r in records)),
        "by_sport": dict(Counter(s for r in records for s in r.get("sports", []))),
        "by_season_phase": dict(Counter(r.get("season_phase", "unknown") for r in records)),
    }
    print(json.dumps(stats, indent=2))
    return stats


def ingest(raw_entries: list[dict]) -> dict:
    # The main function. Pass it a list of data points, it saves them to the repository.
    # Builds each record using schema.py, then calls append_records to save them.
    records = [build_record(**entry) for entry in raw_entries]
    return append_records(records)