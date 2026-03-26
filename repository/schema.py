"""
FanVerse Research Repository — Schema & Record Builder
-------------------------------------------------------
Schema decisions (communicate to team):
  - record_id: SHA-256 hash of (source + text). Deterministic = safe dedup on re-runs.
  - sports: array, not string. One excerpt can reference multiple leagues.
  - url + report_title: required for research reports (provenance).
  - ingested_at: ISO timestamp of when the record entered the repo.
  - week/season_phase: kept from original spec, optional (not all reports are season-specific).
"""

import hashlib
import uuid
from datetime import datetime, date
from typing import Optional

VALID_SOURCES = {"wasserman", "deloitte", "bcg", "nielsen", "mckinsey"}
VALID_SPORTS = {"WNBA", "NWSL", "WTA", "volleyball", "general"}
VALID_SEASON_PHASES = {"preseason", "midseason", "playoff", "finals", "offseason", "unknown"}


def make_record_id(source: str, text: str) -> str:
    """Deterministic ID — same source+text always produces the same hash. Powers deduplication."""
    raw = f"{source.lower()}::{text.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def build_record(
    text: str,
    source: str,
    report_title: str,
    url: str,
    sports: list[str],
    date: Optional[str] = None,
    record_date: Optional[str] = None,
    week: Optional[int] = None,
    season_phase: Optional[str] = "unknown",
    extra: Optional[dict] = None,
) -> dict:
    """
    Build a single repository record. Call this for every excerpt, caption, or data point.

    Args:
        text:           Raw excerpt text from the report.
        source:         One of: wasserman, deloitte, bcg, nielsen, mckinsey.
        report_title:   Full title of the source report.
        url:            URL or file path where the report was found.
        sports:         List of sports this excerpt relates to. Use ["general"] if non-specific.
        record_date:    Date string YYYY-MM-DD. Defaults to today if not provided.
        week:           Week number if season-specific, else None.
        season_phase:   One of: preseason, midseason, playoff, finals, offseason, unknown.
        extra:          Any additional fields you want to attach (flexible).
    """
    source = source.lower().strip()
    assert source in VALID_SOURCES, f"Unknown source: {source}. Must be one of {VALID_SOURCES}"

    sports = [s.strip() for s in sports]
    for s in sports:
        assert s in VALID_SPORTS, f"Unknown sport: {s}. Must be one of {VALID_SPORTS}"

    return {
        "record_id": make_record_id(source, text),
        "post_id": str(uuid.uuid4()),           # unique per ingestion run (for downstream reference)
        "text": text.strip(),
        "source": source,
        "report_title": report_title,
        "url": url,
        "sports": sports,
        "date": record_date or date or __import__('datetime').date.today().isoformat(),
        "week": week,
        "season_phase": season_phase or "unknown",
        "ingested_at": datetime.utcnow().isoformat() + "Z",
        **(extra or {}),
    }