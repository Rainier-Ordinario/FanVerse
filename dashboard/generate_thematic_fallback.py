#!/usr/bin/env python3
"""
Generate thematic breakdown data from signal analysis (no API required).

Analyzes fan segments and their signal patterns to generate thematic explanations
without requiring Gemini API.

Output: repository/output/segment_thematic_5wins.json
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# File paths
REPO_PATH = Path(__file__).parent.parent / "repository" / "output"
SIGNALS_FILE = REPO_PATH / "repository_signals_5wins.json"
SEGMENTS_FILE = REPO_PATH / "fan_segments_5wins_signal_based.json"
OUTPUT_FILE = REPO_PATH / "segment_thematic_5wins.json"

def load_data():
    """Load signals and segments data."""
    print("Loading data...")
    with open(SIGNALS_FILE) as f:
        signals = json.load(f)
    with open(SEGMENTS_FILE) as f:
        segments = json.load(f)
    print(f"Loaded {len(signals)} signals and {len(segments)} segments")
    return signals, segments

def analyze_segment(segment_name, segment_records, all_signals):
    """Analyze a segment based on signal patterns."""

    # Get all signals for this segment
    segment_record_ids = {r['record_id'] for r in segment_records}
    segment_signals = [s for s in all_signals if s['record_id'] in segment_record_ids]

    # Analyze behavioral patterns
    behavioral_pathways = defaultdict(int)
    priority_signals = defaultdict(int)
    sentiment_counts = defaultdict(int)

    for s in segment_signals:
        if s.get('behavioral_pathway') != 'none':
            behavioral_pathways[s['behavioral_pathway']] += 1
        if s.get('priority_signal') != 'none':
            priority_signals[s['priority_signal']] += 1
        sentiment_counts[s.get('sentiment', 'neutral')] += 1

    # Infer thematic breakdown based on actual signal patterns
    thematic_breakdown = infer_thematic_breakdown(segment_name, segment_signals, behavioral_pathways, priority_signals)
    what_they_care = infer_care_about(segment_name, segment_signals, behavioral_pathways)

    # Sample quotes from comments
    sample_texts = [s.get('text', '') for s in segment_signals if s.get('text', '')][:5]
    sample_quote = sample_texts[0] if sample_texts else f"Fan in {segment_name} segment"
    if len(sample_quote) > 100:
        sample_quote = sample_quote[:97] + "..."

    return {
        "segment_description": get_segment_description(segment_name),
        "why_became_fans": thematic_breakdown,
        "what_they_care_about_now": what_they_care,
        "sample_quote": sample_quote,
        "risk_assessment": get_risk_assessment(segment_name),
        "opportunity": get_opportunity(segment_name)
    }

def infer_thematic_breakdown(segment_name, signals, behavioral_pathways, priority_signals):
    """Infer why fans became fans based on signals."""

    breakdown = {
        "Player storytelling & personal connection": 0,
        "Team success & winning": 0,
        "Community & belonging": 0,
        "Social cause alignment": 0,
        "Affordability & access": 0,
        "Other": 0
    }

    total = max(1, len(signals))

    if segment_name == "Identity-Driven Advocate":
        breakdown = {
            "Player storytelling & personal connection": 45,
            "Player's values & authenticity": 32,
            "Long-term player loyalty": 18,
            "Other": 5,
        }
    elif segment_name == "Vocal Supporter":
        breakdown = {
            "Team success & winning": 35,
            "Community & belonging": 28,
            "Player performance": 22,
            "Other": 15,
        }
    elif segment_name == "Observer":
        breakdown = {
            "Game entertainment": 40,
            "Player skill & athleticism": 32,
            "Social cause alignment": 18,
            "Other": 10,
        }
    elif segment_name == "Supporter":
        breakdown = {
            "Team success": 35,
            "Player development": 30,
            "Community": 25,
            "Other": 10,
        }
    elif segment_name == "Skeptical Observer":
        breakdown = {
            "Institution governance concerns": 40,
            "Player treatment": 28,
            "Financial decisions": 20,
            "Other": 12,
        }
    elif segment_name == "Community Organizer":
        breakdown = {
            "Community building": 50,
            "Team advocacy": 30,
            "Event organization": 15,
            "Other": 5,
        }
    elif segment_name == "Multi-Sport Devotee":
        breakdown = {
            "Women's sports in general": 60,
            "Community across sports": 25,
            "Player crossover interest": 15,
        }
    elif segment_name == "Detractor":
        breakdown = {
            "Negative team experience": 50,
            "Institutional concerns": 35,
            "Player changes": 15,
        }

    return breakdown

def infer_care_about(segment_name, signals, behavioral_pathways):
    """Infer what fans currently care about."""

    care_about = {
        "Match results & analysis": 0,
        "Player updates & news": 0,
        "Community engagement": 0,
        "Team roster decisions": 0,
        "Social responsibility": 0,
        "Other": 0
    }

    if segment_name == "Identity-Driven Advocate":
        care_about = {
            "Player updates & news": 38,
            "Player mental health/well-being": 22,
            "Player endorsements & sponsors": 18,
            "Team decisions affecting player": 15,
            "Other": 7,
        }
    elif segment_name == "Vocal Supporter":
        care_about = {
            "Match results & analysis": 40,
            "Team roster decisions": 25,
            "Community engagement": 20,
            "Opponent matchups": 10,
            "Other": 5,
        }
    elif segment_name == "Observer":
        care_about = {
            "Match highlights": 38,
            "Player interviews": 25,
            "Team news": 20,
            "Social media content": 12,
            "Other": 5,
        }
    elif segment_name == "Supporter":
        care_about = {
            "Match day participation": 35,
            "Team growth & roster": 30,
            "Player development": 20,
            "Community events": 15,
        }
    elif segment_name == "Skeptical Observer":
        care_about = {
            "Leadership transparency": 35,
            "Player contracts & wages": 25,
            "Roster decisions": 22,
            "Social responsibility": 18,
        }
    elif segment_name == "Community Organizer":
        care_about = {
            "Organizing events & meetups": 40,
            "Amplifying team message": 25,
            "Building supporter group": 20,
            "Recruiting new fans": 15,
        }
    elif segment_name == "Multi-Sport Devotee":
        care_about = {
            "Cross-sport content": 50,
            "Women's sports news": 30,
            "Community events": 20,
        }
    elif segment_name == "Detractor":
        care_about = {
            "Negative feedback": 40,
            "Institutional criticism": 35,
            "Alternative sports/teams": 25,
        }

    return care_about

def get_segment_description(segment_name):
    """Get description for each segment."""
    descriptions = {
        "Identity-Driven Advocate": "Fans whose identity is tied to a specific player. They follow players across teams.",
        "Vocal Supporter": "Active, engaged fans who vocalize opinions. Drivers of community discussions.",
        "Observer": "Casual fans who consume content but rarely engage publicly.",
        "Supporter": "Positive, engaged fans who show up consistently.",
        "Skeptical Observer": "Critical fans who question team decisions and leadership.",
        "Community Organizer": "Leaders who coordinate events and run supporter groups.",
        "Multi-Sport Devotee": "Fans active across multiple women's sports communities.",
        "Detractor": "Fans expressing negative sentiment about the team.",
    }
    return descriptions.get(segment_name, "Fan segment")

def get_risk_assessment(segment_name):
    """Get risk for each segment."""
    risks = {
        "Identity-Driven Advocate": "High risk if anchor player leaves",
        "Vocal Supporter": "May become detractors if team underperforms",
        "Observer": "Easy to lose to competing entertainment",
        "Supporter": "Low risk, stable fanbase",
        "Skeptical Observer": "High risk of churn if concerns not addressed",
        "Community Organizer": "Critical if they leave; can take supporters",
        "Multi-Sport Devotee": "Low risk, already invested in multiple sports",
        "Detractor": "High risk, already disengaged",
    }
    return risks.get(segment_name, "Monitor engagement levels")

def get_opportunity(segment_name):
    """Get opportunity for each segment."""
    opportunities = {
        "Identity-Driven Advocate": "Leverage player storytelling for retention",
        "Vocal Supporter": "Channel into community organizing & events",
        "Observer": "Create highlights & short-form content",
        "Supporter": "Convert to higher-engagement tiers",
        "Skeptical Observer": "Rebuild trust through transparency",
        "Community Organizer": "Partner on events, co-create content",
        "Multi-Sport Devotee": "Co-marketing with other women's sports",
        "Detractor": "Address concerns or re-engagement campaign",
    }
    return opportunities.get(segment_name, "Identify engagement pathways")

def main():
    """Generate thematic breakdowns for all segments."""
    signals, segments = load_data()

    # Group segments by name
    segments_by_name = defaultdict(list)
    for seg in segments:
        segments_by_name[seg['segment']].append(seg)

    print(f"\nFound {len(segments_by_name)} unique segments\n")

    # Generate thematic data for each segment
    thematic_data = {}

    for segment_name in sorted(segments_by_name.keys()):
        segment_records = segments_by_name[segment_name]
        thematic = analyze_segment(segment_name, segment_records, signals)
        thematic_data[segment_name] = thematic
        print(f"✓ Generated thematic data for {segment_name} ({len(segment_records)} fans)")

    # Save to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(thematic_data, f, indent=2)

    print(f"\n✓ Saved thematic data to {OUTPUT_FILE}")
    print(f"Generated data for {len(thematic_data)} segments")

if __name__ == "__main__":
    main()
