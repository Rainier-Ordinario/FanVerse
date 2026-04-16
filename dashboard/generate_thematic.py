#!/usr/bin/env python3
"""
Generate thematic breakdown data using Gemini API.

This script analyzes fan segments and their signal patterns to generate
thematic explanations of why fans became fans and what they care about.

Output: repository/output/segment_thematic_5wins.json
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)

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
    """Use Gemini to analyze a segment and generate thematic breakdown."""

    # Collect segment data
    segment_signals = [s for s in all_signals if s['record_id'] in [r['record_id'] for r in segment_records]]

    # Build context about this segment
    sample_texts = [s.get('text', '') for s in segment_signals[:10] if s.get('text')]
    behavioral_pathways = defaultdict(int)
    priority_signals = defaultdict(int)

    for s in segment_signals:
        if s.get('behavioral_pathway') != 'none':
            behavioral_pathways[s['behavioral_pathway']] += 1
        if s.get('priority_signal') != 'none':
            priority_signals[s['priority_signal']] += 1

    sentiment_dist = defaultdict(int)
    for s in segment_signals:
        sentiment_dist[s.get('sentiment', 'neutral')] += 1

    # Create prompt for Gemini
    prompt = f"""
You are analyzing fan segments for a women's sports platform. Analyze this segment data and provide insights.

SEGMENT: {segment_name}
TOTAL FANS: {len(segment_records)}

KEY BEHAVIORS:
- Behavioral pathways: {dict(behavioral_pathways)}
- Priority signals: {dict(priority_signals)}
- Sentiment distribution: {dict(sentiment_dist)}

SAMPLE FAN COMMENTS:
{chr(10).join([f'- "{text[:100]}"' for text in sample_texts if text])}

Generate a JSON response with this exact structure (no markdown, pure JSON):
{{
  "segment_description": "1-2 sentence description of this fan type",
  "why_became_fans": {{
    "Player storytelling & personal connection": <percentage>,
    "Team success & winning": <percentage>,
    "Community & belonging": <percentage>,
    "Social cause alignment": <percentage>,
    "Affordability & access": <percentage>,
    "Other": <percentage>
  }},
  "what_they_care_about_now": {{
    "Player updates & news": <percentage>,
    "Match results & analysis": <percentage>,
    "Community engagement": <percentage>,
    "Team roster decisions": <percentage>,
    "Social responsibility": <percentage>,
    "Other": <percentage>
  }},
  "sample_quote": "A representative quote from this segment",
  "risk_assessment": "1 sentence describing the key risk for this segment",
  "opportunity": "1 sentence describing the key opportunity for this segment"
}}

Percentages must sum to 100. Be specific to the actual data shown above.
"""

    print(f"Analyzing {segment_name}...")

    try:
        # Try different model names
        model_names = ['gemini-2.0-flash', 'gemini-pro', 'gemini-1.5-pro']
        response = None

        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                break
            except Exception as e:
                continue

        if response is None:
            print(f"✗ No available models for {segment_name}")
            return None

        # Parse the response
        response_text = response.text

        # Try to extract JSON from the response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1

        if start >= 0 and end > start:
            json_str = response_text[start:end]
            result = json.loads(json_str)
            print(f"✓ Generated thematic data for {segment_name}")
            return result
        else:
            print(f"✗ Could not extract JSON from response for {segment_name}")
            return None

    except Exception as e:
        print(f"✗ Error analyzing {segment_name}: {str(e)}")
        return None

def main():
    """Generate thematic breakdowns for all segments."""

    signals, segments = load_data()

    # Group segments by name
    segments_by_name = defaultdict(list)
    for seg in segments:
        segments_by_name[seg['segment']].append(seg)

    print(f"\nFound {len(segments_by_name)} unique segments")

    # Generate thematic data for each segment
    thematic_data = {}

    for segment_name in sorted(segments_by_name.keys()):
        segment_records = segments_by_name[segment_name]
        thematic = analyze_segment(segment_name, segment_records, signals)

        if thematic:
            thematic_data[segment_name] = thematic

    # Save to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(thematic_data, f, indent=2)

    print(f"\n✓ Saved thematic data to {OUTPUT_FILE}")
    print(f"Generated data for {len(thematic_data)} segments")

if __name__ == "__main__":
    main()
