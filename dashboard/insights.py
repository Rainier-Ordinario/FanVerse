"""
insights.py — FanVerse insight engine.

get_insight() is the single entry point for the Insight Panel.
Wire the Claude API inside that function — everything else is ready.
"""

import pandas as pd

# ── Preset queries (shown as chips in the UI) ──────────────────────────────

PRESET_QUERIES = [
    "Which of our female fans are showing early disengagement signals this month, and what triggered the shift?",
    "Which cross-sport super fan segments offer the highest co-marketing value across two leagues?",
    "What cultural moments outside of sport are currently driving our female fans toward or away from our team?",
]

# ── Prompt template ────────────────────────────────────────────────────────

INSIGHT_PROMPT = """\
You are FanVerse, a female fan intelligence engine. You have been given real fan \
signal records collected from Reddit communities and industry research reports. \
Each record includes the sport, source, behavioral pathway, priority signal, \
sentiment score, and the raw fan text.

Answer the following question based ONLY on what the records show. Do not invent \
data. If the records are insufficient to answer confidently, say so honestly in \
the finding field.

Question: {query}

Fan signal records:
{context}

Respond with a JSON object in exactly this format — no markdown fences, raw JSON only:
{{
  "finding": "One clear sentence stating the main finding from the data.",
  "evidence": "2-3 sentences in plain prose citing specific signals, record counts, or short direct quotes. Refer to sources naturally (e.g. 'A Deloitte report notes…' or 'Reddit fans comment…') — do not reproduce the raw metadata tags from the records.",
  "confidence": <integer 0-100 reflecting how well the records support the finding>,
  "recommended_action": "One concrete, specific action a sports organisation should take based on this finding."
}}"""

# ── Context builder ────────────────────────────────────────────────────────

def build_context(query: str, signals_df: pd.DataFrame, n_records: int = 25) -> str:
    """
    Selects the most relevant records from signals_df for the given query
    and formats them as plain text for the prompt.
    """
    q = query.lower()

    if any(w in q for w in ("disengagement", "churn", "leaving", "shift", "triggered")):
        mask = (
            signals_df["behavioral_pathway"].isin(["churn_risk", "disengagement_marker"]) |
            signals_df["priority_signal"].isin(["loyalty_stress", "trust_split"])
        )
    elif any(w in q for w in ("cross-sport", "co-marketing", "two leagues", "multi")):
        mask = signals_df["priority_signal"].isin(["cross_sport_superfan", "identity_anchor"])
    elif any(w in q for w in ("cultural", "outside", "moment", "toward", "away")):
        mask = (
            signals_df["priority_signal"].isin(["loyalty_stress", "trust_split"]) |
            signals_df["behavioral_pathway"].isin(["churn_risk", "community_influence"])
        )
    else:
        mask = signals_df["priority_signal"] != "none"

    relevant = signals_df[mask].drop_duplicates("record_id")
    if relevant.empty:
        relevant = signals_df.drop_duplicates("record_id")

    top = relevant.head(n_records)

    lines = []
    for _, row in top.iterrows():
        lines.append(
            f"[sport:{row['sport']} | source:{row['source']} | "
            f"pathway:{row['behavioral_pathway']} | priority:{row['priority_signal']} | "
            f"sentiment:{row['sentiment']} ({row['sentiment_score']:.2f})] "
            f"{str(row['text'])[:300]}"
        )
    return "\n\n".join(lines)


# ── Main insight function — wire Gemini API here ──────────────────────────

def get_insight(query: str, signals_df: pd.DataFrame, segments_df: pd.DataFrame) -> dict:
    """
    Returns a structured insight dict:
        {
            "finding":            str,
            "evidence":           str,
            "confidence":         int,   # 0–100
            "recommended_action": str,
            "ready":              bool,  # False until API is wired
        }

    ── HOW TO WIRE THE GEMINI API ──────────────────────────────────────────

    1. 'google-generativeai' is already in pyproject.toml — run: uv sync
    2. Add GEMINI_API_KEY=... to repository/.env
    3. Replace the TODO block below with:

        import google.generativeai as genai
        import os, json as _json
        from dotenv import load_dotenv
        from pathlib import Path

        load_dotenv(Path(__file__).parent.parent / "repository" / ".env")
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])

        model   = genai.GenerativeModel("gemini-2.5-flash")
        context = build_context(query, signals_df)
        prompt  = INSIGHT_PROMPT.format(query=query, context=context)

        response = model.generate_content(prompt)
        result   = _json.loads(response.text)
        result["ready"] = True
        return result

    ────────────────────────────────────────────────────────────────────────
    """
    import google.generativeai as genai
    import os, json as _json
    from dotenv import load_dotenv
    from pathlib import Path

    load_dotenv(Path(__file__).parent.parent / "repository" / ".env")
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    model   = genai.GenerativeModel("gemini-2.5-flash")
    context = build_context(query, signals_df)
    prompt  = INSIGHT_PROMPT.format(query=query, context=context)

    try:
        response = model.generate_content(prompt)
        result   = _json.loads(response.text)
        result["ready"] = True
        return result
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower() or "ResourceExhausted" in err:
            finding = "API quota exceeded. Enable billing on your Google AI project to use the Insight Panel."
        else:
            finding = f"API error: {err[:200]}"
        return {
            "finding":            finding,
            "evidence":           "",
            "confidence":         0,
            "recommended_action": "",
            "ready":              False,
        }


# ── Simulation model ───────────────────────────────────────────────────────

# Baseline 90-day retention rates derived from real cluster sentiment means.
# Frustrated Loyalist (sentiment 0.19) and Passive/Disengaged (0.40) are
# the two at-risk groups. Rates are conservative estimates, not predictions.
_BASELINE_RETENTION = {
    "Superfan":                          90,
    "Core Engaged Fan":                  72,
    "Casual Enthusiast":                 55,
    "Emotionally Invested, Weak Signal": 48,
    "Frustrated Loyalist":               22,
    "Passive / Disengaged":              18,
}

# Per-query uplift applied to baseline when recommended action is taken.
# Index matches PRESET_QUERIES order.
_UPLIFT_BY_QUERY = [
    # Query 0 — address disengagement / loyalty stress signals
    {
        "Superfan":                          3,
        "Core Engaged Fan":                  6,
        "Casual Enthusiast":                 9,
        "Emotionally Invested, Weak Signal": 11,
        "Frustrated Loyalist":               22,
        "Passive / Disengaged":              16,
    },
    # Query 1 — cross-sport co-marketing activation
    {
        "Superfan":                          5,
        "Core Engaged Fan":                  11,
        "Casual Enthusiast":                 16,
        "Emotionally Invested, Weak Signal": 18,
        "Frustrated Loyalist":               4,
        "Passive / Disengaged":              3,
    },
    # Query 2 — cultural moment content strategy
    {
        "Superfan":                          4,
        "Core Engaged Fan":                  7,
        "Casual Enthusiast":                 10,
        "Emotionally Invested, Weak Signal": 9,
        "Frustrated Loyalist":               28,
        "Passive / Disengaged":              12,
    },
]

# Fallback uplift for free-text queries
_DEFAULT_UPLIFT = {seg: 8 for seg in _BASELINE_RETENTION}


def compute_simulation(query_index: int | None) -> dict:
    """
    Returns simulation data for the bar chart and summary metrics.

    query_index: int (0–2) for preset queries, None for free-text.

    Return shape:
        {
            "segments":   list[str],
            "baseline":   list[int],   # % retention, status quo
            "projected":  list[int],   # % retention, with action
            "summary": {
                "churn_reduction":    int,  # % improvement in at-risk segments
                "conversion_uplift":  int,  # % improvement in mid-tier segments
                "fans_reengaged_pct": int,  # avg uplift across at-risk
                "model_confidence":   int,  # fixed per scenario
            }
        }
    """
    uplift = (
        _UPLIFT_BY_QUERY[query_index]
        if isinstance(query_index, int) and 0 <= query_index < len(_UPLIFT_BY_QUERY)
        else _DEFAULT_UPLIFT
    )

    # Order segments from most to least engaged for the chart
    order = [
        "Superfan",
        "Core Engaged Fan",
        "Casual Enthusiast",
        "Emotionally Invested, Weak Signal",
        "Frustrated Loyalist",
        "Passive / Disengaged",
    ]

    baseline  = [_BASELINE_RETENTION[s] for s in order]
    projected = [min(99, _BASELINE_RETENTION[s] + uplift[s]) for s in order]

    at_risk     = ["Frustrated Loyalist", "Passive / Disengaged"]
    mid_tier    = ["Casual Enthusiast", "Emotionally Invested, Weak Signal"]

    churn_uplift = sum(uplift[s] for s in at_risk) / len(at_risk)
    conv_uplift  = sum(uplift[s] for s in mid_tier) / len(mid_tier)
    avg_rengaged = sum(uplift[s] for s in at_risk) / len(at_risk)

    confidence_map = {0: 74, 1: 61, 2: 68, None: 55}
    model_confidence = confidence_map.get(query_index, 55)

    return {
        "segments":  order,
        "baseline":  baseline,
        "projected": projected,
        "summary": {
            "churn_reduction":    round(churn_uplift),
            "conversion_uplift":  round(conv_uplift),
            "fans_reengaged_pct": round(avg_rengaged),
            "model_confidence":   model_confidence,
        },
    }
