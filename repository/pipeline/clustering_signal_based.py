#!/usr/bin/env python3
"""
Generate fan segments using signal-based classification.

This approach maps FanVerse behavioral and priority signals directly to
meaningful fan segments, eliminating the information loss of K-Means clustering.

Usage: python3 clustering_signal_based.py <client_name>
Example: python3 clustering_signal_based.py 5wins
         python3 clustering_signal_based.py allez_sports
"""

import json
import sys
from pathlib import Path

import pandas as pd

# ---- CLIENT CONFIGURATION ----
if len(sys.argv) < 2:
    print("Usage: python3 clustering_signal_based.py <client_name>")
    print("Example: python3 clustering_signal_based.py 5wins")
    sys.exit(1)

CLIENT = sys.argv[1]
REPO_PATH = Path(__file__).parent.parent / "output" / f"repository_signals_{CLIENT}.json"
OUTPUT_PATH = Path(__file__).parent.parent / "output" / f"fan_segments_{CLIENT}_signal_based.json"

if not REPO_PATH.exists():
    print(f"ERROR: {REPO_PATH} not found")
    sys.exit(1)

# ---- LOAD DATA ----
print(f"Loading {CLIENT} signals from {REPO_PATH}...")
with open(REPO_PATH) as f:
    data = json.load(f)

df = pd.DataFrame(data)
print(f"Loaded {len(df)} records")

# Filter: remove reddit posts tagged only as 'general'
mask_drop = (df["source"] == "reddit") & (df["sports"].apply(lambda x: x == ["general"]))
df_filtered = df[~mask_drop].reset_index(drop=True)
print(f"After filtering: {len(df_filtered)} records")

# ---- SIGNAL-BASED SEGMENTATION ----
def assign_segment(row):
    """Assign segment based on priority_signal hierarchy."""

    # Priority signals take precedence (these are most meaningful)
    if row["priority_signal"] == "identity_anchor":
        return "Identity-Driven Advocate"
    elif row["priority_signal"] == "conversion_moment":
        return "New Discovery"
    elif row["priority_signal"] == "cross_sport_superfan":
        return "Multi-Sport Devotee"
    elif row["priority_signal"] == "loyalty_stress":
        return "At-Risk Loyalist"
    elif row["priority_signal"] == "trust_split":
        return "Skeptical Observer"

    # Secondary: behavioral pathway signals
    elif row["behavioral_pathway"] == "identity_attachment":
        return "Identity-Driven Advocate"
    elif row["behavioral_pathway"] == "loyalty_signal":
        return "Vocal Supporter"
    elif row["behavioral_pathway"] == "conversion_trigger":
        return "New Discovery"
    elif row["behavioral_pathway"] == "community_influence":
        return "Community Organizer"
    elif row["behavioral_pathway"] == "churn_risk":
        return "Disengaged"

    # Fallback: sentiment-based classification
    elif row["sentiment"] == "positive":
        return "Supporter"
    elif row["sentiment"] == "neutral":
        return "Observer"
    else:  # negative
        return "Detractor"


df_filtered["segment"] = df_filtered.apply(assign_segment, axis=1)

# ---- EXPORT ----
export_cols = [
    "record_id",
    "source",
    "sports",
    "sentiment",
    "sentiment_score",
    "emotional_affinity_score",
    "confidence_score",
    "behavioral_pathway",
    "priority_signal",
    "segment"
]

df_export = df_filtered[export_cols].copy()

with open(OUTPUT_PATH, "w") as f:
    json.dump(df_export.to_dict(orient="records"), f, indent=2)

print(f"\nDone. {len(df_export)} segments saved to {OUTPUT_PATH}")

# Print summary
print(f"\nSignal-based segment breakdown:")
segment_counts = df_export["segment"].value_counts()
for segment in sorted(segment_counts.index):
    count = segment_counts[segment]
    pct = round(100 * count / len(df_export), 1)
    print(f"  {segment}: {count} ({pct}%)")

# Show what changed
print(f"\n--- Signal Distribution ---")
print(f"Priority signals:")
for sig in sorted(df_export["priority_signal"].unique()):
    if sig != "none":
        count = len(df_export[df_export["priority_signal"] == sig])
        pct = round(100 * count / len(df_export), 1)
        print(f"  {sig}: {count} ({pct}%)")

print(f"\nBehavioral pathways:")
for sig in sorted(df_export["behavioral_pathway"].unique()):
    if sig != "none":
        count = len(df_export[df_export["behavioral_pathway"] == sig])
        pct = round(100 * count / len(df_export), 1)
        print(f"  {sig}: {count} ({pct}%)")
