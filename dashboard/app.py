"""
app.py — FanVerse 3-Layer Dashboard (Mock Data - Design Validation)

Layers:
- Layer 1 (The Brief): Ask FanVerse + 4 signal status indicators
- Layer 2 (Signal Map): 5 signal panels with drill-downs
- Layer 3 (Intelligence): Cultural Feed, Pattern Map, Simulation, Daily Pulse

Run: streamlit run dashboard/app.py
"""

import streamlit as st
import plotly.express as px

# ── Page Config ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="FanVerse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ──────────────────────────────────────────────────────────────────

BG = "#ffffff"
CARD_BG = "#f9fafb"
CARD_BORDER = "#e5e7eb"
TEXT = "#111827"
SUBTEXT = "#6b7280"
GRID = "#f0f0f0"
PRIMARY = "#10b981"  # Green
SECONDARY = "#e0e7ff"  # Light purple for active nav

st.markdown(f"""
<style>
  html, body, [class*="css"] {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: {BG};
    color: {TEXT};
  }}
  #MainMenu, footer, header {{ visibility: hidden; }}
  [data-testid="stToolbar"] {{ display: none; }}
  [data-testid="stHeader"] {{ display: none; }}
  .stApp {{ background-color: {BG}; }}
  .block-container {{ background-color: {BG}; padding: 1.5rem 2rem; }}

  /* Ensure sidebar is visible */
  section[data-testid="stSidebar"] {{ display: block !important; }}
  .sidebar-content {{ display: block !important; }}

  /* Hide sidebar collapse button */
  button[aria-label="Close sidebar"] {{ display: none !important; }}
  [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}


  .signal-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
  }}

  .signal-panel {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .signal-panel:hover {{
    border-color: {PRIMARY};
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }}

  .ask-input {{
    background: {CARD_BG};
    border: 2px solid {PRIMARY};
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
  }}

  .status-badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }}
  .status-active {{ background: #dcfce7; color: #16a34a; }}
  .status-emerging {{ background: #fef3c7; color: #f59e0b; }}
  .status-stable {{ background: #f3f4f6; color: #6b7280; }}
  .status-present {{ background: #eff6ff; color: {PRIMARY}; }}
  .status-widening {{ background: #fee2e2; color: #dc2626; }}

  .metric-value {{
    font-size: 28px;
    font-weight: 700;
    color: {PRIMARY};
    line-height: 1;
  }}

  .trend-up {{ color: #16a34a; }}
  .trend-down {{ color: #dc2626; }}
  .trend-stable {{ color: #6b7280; }}

  .stTabs [data-baseweb="tab"] {{
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }}
  .stTabs [aria-selected="true"] {{
    color: {PRIMARY} !important;
    border-bottom: 2px solid {PRIMARY} !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation (MUST BE EARLY) ──────────────────────────────────────

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Overview"

if "drill_down_signal" not in st.session_state:
    st.session_state["drill_down_signal"] = None

if "viewing_segment" not in st.session_state:
    st.session_state["viewing_segment"] = None

with st.sidebar:
    col = st.columns([1])
    with col[0]:
        st.markdown(f"# :green[FanVerse]")
    st.markdown("**Navigation**")
    st.divider()

    pages = ["Overview", "Signals", "Segments", "Cultural Feed", "Insights"]

    for page in pages:
        is_active = st.session_state["current_page"] == page

        if is_active:
            st.button(page, use_container_width=True, key=f"nav_{page}", disabled=True)
        else:
            if st.button(page, use_container_width=True, key=f"nav_{page}"):
                st.session_state["current_page"] = page
                st.session_state["drill_down_signal"] = None
                st.rerun()

# ── Mock Data ──────────────────────────────────────────────────────────────

def generate_mock_signals():
    """Generate mock signal data."""
    return {
        "loyalty_stress": {
            "title": "Loyalty Risk",
            "metric": "18%",
            "status": "Active",
            "status_class": "status-active",
            "trend": "↑",
            "trend_class": "trend-up",
            "finding": "What percentage of the fan community is showing early disengagement signals right now?",
            "description": "18% showing early disengagement language. ⚠️ Early warning: churn visible here before it shows in ticket data.",
        },
        "identity_anchor": {
            "title": "Identity Anchor",
            "metric": "5",
            "status": "Stable",
            "status_class": "status-stable",
            "trend": "—",
            "trend_class": "trend-stable",
            "finding": "Which player carries the most emotional weight in the community?",
            "description": "Caroline Seger is the primary identity anchor. Stable over 30 days. 🔑 Key retention lever.",
        },
        "conversion_moment": {
            "title": "Conversion Window",
            "metric": "12",
            "status": "Emerging",
            "status_class": "status-emerging",
            "trend": "↑",
            "trend_class": "trend-up",
            "finding": "How many fans are at the moment where they could move from casual to committed?",
            "description": "12 new fans converting this week via player storytelling. 📊 Actionable window: activate now.",
        },
        "cross_sport_superfan": {
            "title": "Cross-Sport Super Fan",
            "metric": "4%",
            "status": "Present",
            "status_class": "status-present",
            "trend": "—",
            "trend_class": "trend-stable",
            "finding": "Which fans are active across multiple women's sports communities?",
            "description": "4% of fanbase active across women's sports. 🤝 Co-marketing opportunity identified.",
        },
        "trust_split": {
            "title": "Trust Gap",
            "metric": "54 pts",
            "status": "Widening",
            "status_class": "status-widening",
            "trend": "↓",
            "trend_class": "trend-down",
            "finding": "What is the spread between player-directed and institution-directed sentiment?",
            "description": "Players +72%, Institution +18%. Gap widening. ⚠️ Institutional trust problem emerging.",
        },
    }

def generate_segment_thematic_data(segment_name):
    """Generate mock thematic breakdown data for a segment."""
    segment_data = {
        "Identity-Driven Advocate": {
            "description": "Fans whose identity is deeply tied to a specific player or team. They follow players across teams and platforms.",
            "count": 156,
            "pct": 28,
            "thematic": {
                "Player storytelling & personal connection": 45,
                "Player's values & authenticity": 32,
                "Long-term player loyalty": 18,
                "Other": 5,
            },
            "what_they_care_about": {
                "Player updates & news": 38,
                "Player mental health/well-being": 22,
                "Player endorsements & sponsors": 18,
                "Team decisions affecting player": 15,
                "Other": 7,
            },
            "sample_quotes": [
                '"She\'s the reason I watch. When she leaves, I follow."',
                '"I\'ve been following her since [previous team]. Her authenticity is why I\'m here."',
                '"I care about her journey, not just the wins."',
            ],
            "risk": "High risk if anchor player leaves",
            "opportunity": "Leverage player storytelling for retention",
        },
        "Vocal Supporter": {
            "description": "Active, engaged fans who vocalize their opinions in communities. They drive word-of-mouth and community discussions.",
            "count": 112,
            "pct": 20,
            "thematic": {
                "Team success & winning": 35,
                "Community & belonging": 28,
                "Player performance": 22,
                "Other": 15,
            },
            "what_they_care_about": {
                "Match results & analysis": 40,
                "Team roster decisions": 25,
                "Community engagement": 20,
                "Opponent matchups": 10,
                "Other": 5,
            },
            "sample_quotes": [
                '"Let\'s analyze that last play!"',
                '"The community here is amazing."',
                '"Our roster is stacked this year."',
            ],
            "risk": "May become detractors if team underperforms",
            "opportunity": "Channel into community organizing & events",
        },
        "Observer": {
            "description": "Casual fans who consume content but rarely engage publicly. Often lurkers in communities.",
            "count": 98,
            "pct": 18,
            "thematic": {
                "Game entertainment": 40,
                "Player skill & athleticism": 32,
                "Social cause alignment": 18,
                "Other": 10,
            },
            "what_they_care_about": {
                "Match highlights": 38,
                "Player interviews": 25,
                "Team news": 20,
                "Social media content": 12,
                "Other": 5,
            },
            "sample_quotes": [
                '"Great match! (no further comment)"',
                '"Love watching her play."',
                '"Impressive athleticism."',
            ],
            "risk": "Easy to lose to competing entertainment",
            "opportunity": "Create highlights & short-form content",
        },
        "Supporter": {
            "description": "Positive, engaged fans who show up consistently. Moderate engagement across platforms.",
            "count": 87,
            "pct": 16,
            "thematic": {
                "Team success": 35,
                "Player development": 30,
                "Community": 25,
                "Other": 10,
            },
            "what_they_care_about": {
                "Match day participation": 35,
                "Team growth & roster": 30,
                "Player development": 20,
                "Community events": 15,
            },
            "sample_quotes": [
                '"Rooting for the team!"',
                '"So proud of how she\'s developed."',
                '"Can\'t wait for the next match."',
            ],
            "risk": "Low risk, stable fanbase",
            "opportunity": "Convert to higher-engagement tiers",
        },
        "Skeptical Observer": {
            "description": "Critical fans who question team decisions. Voice doubts about leadership & direction.",
            "count": 65,
            "pct": 12,
            "thematic": {
                "Institution governance concerns": 40,
                "Player treatment": 28,
                "Financial decisions": 20,
                "Other": 12,
            },
            "what_they_care_about": {
                "Leadership transparency": 35,
                "Player contracts & wages": 25,
                "Roster decisions": 22,
                "Social responsibility": 18,
            },
            "sample_quotes": [
                '"Why did they make that decision?"',
                '"Don\'t trust the front office."',
                '"The players deserve better support."',
            ],
            "risk": "High risk of churn if concerns not addressed",
            "opportunity": "Rebuild trust through transparency",
        },
        "Community Organizer": {
            "description": "Leaders who coordinate events, create content, run supporter groups. Highest engagement.",
            "count": 34,
            "pct": 6,
            "thematic": {
                "Community building": 50,
                "Team advocacy": 30,
                "Event organization": 15,
                "Other": 5,
            },
            "what_they_care_about": {
                "Organizing events & meetups": 40,
                "Amplifying team message": 25,
                "Building supporter group": 20,
                "Recruiting new fans": 15,
            },
            "sample_quotes": [
                '"Who wants to organize a watch party?"',
                '"Let\'s get more people involved."',
                '"We need to build this community."',
            ],
            "risk": "Critical if they leave; can take supporters with them",
            "opportunity": "Partner on events, co-create content",
        },
    }
    return segment_data.get(segment_name, {})

def generate_mock_drill_down(signal_key):
    """Generate mock drill-down data for a signal."""
    drill_downs = {
        "loyalty_stress": {
            "posts": [
                {"text": "If they trade her, I'm done with this team. Been a fan for 5 years.", "date": "Apr 12", "source": "Reddit"},
                {"text": "Love the players but the management is making terrible decisions", "date": "Apr 10", "source": "Instagram"},
                {"text": "Can't believe they're letting her go. This is the last straw.", "date": "Apr 8", "source": "X"},
            ],
            "affected_segments": {
                "At-Risk Loyalists": 47,
                "Skeptical Observers": 23,
                "Vocal Supporters": 15,
            },
            "action": "ACTION REQUIRED: 18% of fanbase is at churn risk. Recommended: Community re-engagement campaign within 7 days. If delayed beyond 14 days, conversion becomes much harder. Consider leadership statement + player reassurance content.",
        },
        "identity_anchor": {
            "posts": [
                {"text": "Caroline Seger is the reason I watch this team. Absolute legend.", "date": "Apr 11", "source": "Reddit"},
                {"text": "If she leaves, I leave. Period.", "date": "Apr 9", "source": "Instagram"},
            ],
            "affected_segments": {
                "Identity-Driven Advocates": 82,
                "Vocal Supporters": 34,
            },
            "action": "ACTION REQUIRED: 82% of Identity-Driven Advocates are anchored to one player. Recommended: (1) Secure long-term commitment from anchor player, OR (2) Begin building secondary identity anchors now to prepare for potential departure.",
        },
        "conversion_moment": {
            "posts": [
                {"text": "Just watched her interview and I'm hooked. Subscribing now.", "date": "Apr 13", "source": "YouTube"},
                {"text": "First game I watched and I'm already in love with this sport", "date": "Apr 12", "source": "Reddit"},
            ],
            "affected_segments": {
                "New Discovery": 89,
                "Emerging Fans": 45,
            },
            "action": "ACTION REQUIRED: Conversion window is OPEN right now. Recommended: Immediately amplify player storytelling content (interviews, behind-the-scenes, personal stories). Window closes in 7 days — after that, momentum is lost.",
        },
        "cross_sport_superfan": {
            "posts": [
                {"text": "Love following women's soccer and basketball. Both sports are amazing.", "date": "Apr 10", "source": "Twitter"},
            ],
            "affected_segments": {
                "Multi-Sport Devotee": 100,
            },
            "action": "STRATEGIC OPPORTUNITY: 4% of fanbase actively follows multiple women's sports. Recommended: Launch co-marketing campaign with women's basketball/rugby partners. This segment has high lifetime value and influence.",
        },
        "trust_split": {
            "posts": [
                {"text": "Love the players but the ownership/management is destroying this team.", "date": "Apr 11", "source": "Reddit"},
                {"text": "The girls are incredible. The front office is a joke.", "date": "Apr 9", "source": "Instagram"},
            ],
            "affected_segments": {
                "Skeptical Observers": 67,
                "At-Risk Loyalists": 34,
            },
            "action": "ACTION REQUIRED: Gap is widening. Players are strong (+72%), institution is weak (+18%). Recommended: (1) Public leadership statement addressing governance concerns, (2) Transparency initiative, (3) Fan advisory board. Risk: If unaddressed, this gap will trigger sponsor backlash within 30 days.",
        },
    }
    return drill_downs.get(signal_key, {})

# ── Top Bar ────────────────────────────────────────────────────────────────

col_logo, col_title, col_filters = st.columns([1, 2, 2])

with col_logo:
    st.markdown(f"<div style='font-size:14px;color:{SUBTEXT};'>Mock Data · Design Validation</div>", unsafe_allow_html=True)

with col_filters:
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        period = st.selectbox("Period", ["All Years", "2026", "2025", "2024", "2023", "2022", "2021", "2020"], index=0, label_visibility="collapsed")
    with filter_col2:
        source = st.selectbox(
            "Source",
            ["All Sources", "Reddit", "X", "Instagram", "TikTok", "YouTube", "Substack", "Connect a data source..."],
            index=0,
            label_visibility="collapsed"
        )
        if source == "Connect a data source...":
            st.info("🔄 **Connect Internal Data** — Integrate ticket sales, CRM, or internal systems data alongside community signals. Coming soon.")

st.markdown("---")

# ── Sidebar Navigation ────────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW (LAYER 1)
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state["current_page"] == "Overview":
    st.markdown("## The Brief — What's Happening Right Now")
    st.markdown(f"<span style='font-size:14px;color:{SUBTEXT};'>Real-time insights into fan sentiment, behavior, and growth opportunities. No guesswork. Pure signal.</span>", unsafe_allow_html=True)
    st.markdown("")

    # Ask FanVerse Query Box
    st.markdown("<div class='ask-input'>", unsafe_allow_html=True)
    st.markdown("**Ask FanVerse anything about your fans.**")

    ask_col1, ask_col2 = st.columns([5, 1])
    with ask_col1:
        query = st.text_input(
            "Query",
            placeholder="What's driving engagement? Why are new fans converting?",
            label_visibility="collapsed",
            key="ask_query"
        )
    with ask_col2:
        if st.button("Ask →", use_container_width=True):
            st.info(f"Query received: '{query}' (Claude API not yet connected)")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")

    # Four Signal Status Indicators
    st.markdown("### Signal Status Indicators")
    st.markdown(f"<span style='font-size:12px;color:{SUBTEXT};'>Four critical signals. No scrolling needed. Everything else requires a decision.</span>", unsafe_allow_html=True)

    signals = generate_mock_signals()
    layer1_signals = ["loyalty_stress", "conversion_moment", "identity_anchor", "trust_split"]

    cols = st.columns(2)
    for idx, signal_key in enumerate(layer1_signals):
        col = cols[idx % 2]
        sig = signals.get(signal_key, {})

        with col:
            st.markdown(f"""
            <div class='signal-card'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'>
                    <div style='font-size:16px;font-weight:700;color:{TEXT};'>{sig.get('title', 'N/A')}</div>
                    <span class='status-badge {sig.get('status_class', 'status-stable')}'>{sig.get('status', 'N/A')}</span>
                </div>
                <div style='margin-bottom:12px;'>
                    <div style='font-size:24px;font-weight:700;color:{PRIMARY};'>{sig.get('metric', '0')}</div>
                    <div style='font-size:12px;color:{SUBTEXT};margin-top:4px;'>{sig.get('description', '')}</div>
                </div>
                <div style='font-size:12px;color:{SUBTEXT};'>
                    Trend: <span class='{sig.get('trend_class', 'trend-stable')}'>{sig.get('trend', '—')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SIGNALS (LAYER 2)
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state["current_page"] == "Signals":

    if st.session_state["drill_down_signal"]:
        signals = generate_mock_signals()
        drill_key = st.session_state["drill_down_signal"]
        drill_data = generate_mock_drill_down(drill_key)
        sig = signals[drill_key]

        col_back, col_title, col_status = st.columns([1, 3, 1])
        with col_back:
            if st.button("← Back to Signals", use_container_width=True):
                st.session_state["drill_down_signal"] = None
                st.rerun()

        with col_title:
            st.markdown(f"<h2 style='margin:0;color:{TEXT};'>{sig['title']}</h2>", unsafe_allow_html=True)

        with col_status:
            st.markdown(f"<span class='status-badge {sig['status_class']}'>{sig['status']}</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("")

        st.markdown("### Summary")
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)

        with sum_col1:
            st.metric("Metric", sig['metric'], border=False)

        with sum_col2:
            st.metric("Status", sig['status'], border=False)

        with sum_col3:
            st.metric("Trend", sig['trend'], border=False)

        with sum_col4:
            st.markdown(f"<div style='font-size:12px;color:{SUBTEXT};font-weight:600;margin-bottom:8px;'>KEY FINDING</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:13px;color:{TEXT};'>{sig['finding']}</div>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("---")
        st.markdown("")

        st.markdown("### Specific Posts Driving This Signal")

        for post in drill_data.get("posts", []):
            st.markdown(f"""
            <div style='background:{CARD_BG};border-left:4px solid {PRIMARY};padding:16px;margin-bottom:12px;border-radius:8px;'>
                <div style='font-size:11px;color:{SUBTEXT};margin-bottom:8px;font-weight:500;'>{post['date']} • {post['source']}</div>
                <div style='font-size:14px;color:{TEXT};line-height:1.6;'>{post['text']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("---")
        st.markdown("")

        st.markdown("### Affected Fan Segments")

        seg_data = drill_data.get("affected_segments", {})
        if seg_data:
            seg_cols = st.columns(len(seg_data))
            for idx, (segment, count) in enumerate(seg_data.items()):
                with seg_cols[idx]:
                    st.markdown(f"""
                    <div style='background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:8px;padding:16px;text-align:center;'>
                        <div style='font-weight:700;color:{PRIMARY};font-size:24px;'>{count}</div>
                        <div style='font-size:12px;color:{SUBTEXT};margin-top:6px;'>{segment}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("---")
        st.markdown("")

        st.markdown("### Why These Fans Became Fans (Thematic Breakdown)")
        st.markdown(f"<span style='font-size:12px;color:{SUBTEXT};'>Updated monthly to track composition shifts</span>", unsafe_allow_html=True)

        st.info("💡 Thematic breakdown will be populated when you drill into specific segments.")

        st.markdown("")
        st.markdown("---")
        st.markdown("")

        st.markdown("### Recommended Action")

        action_text = drill_data.get("action", "No action recommended at this time.")

        action_colors = {
            "loyalty_stress": ("#FEE2E2", "#991B1B"),
            "identity_anchor": ("#EFF6FF", "#1E40AF"),
            "conversion_moment": ("#FEF3C7", "#854D0E"),
            "cross_sport_superfan": ("#E8F5E9", "#1B4D3E"),
            "trust_split": ("#FEE2E2", "#991B1B"),
        }

        bg_color, text_color = action_colors.get(drill_key, ("#F3F4F6", "#374151"))

        st.markdown(f"""
        <div style='background:{bg_color};border-left:4px solid {text_color};padding:20px;border-radius:8px;'>
            <div style='color:{text_color};font-weight:700;font-size:14px;margin-bottom:8px;'>ACTION REQUIRED</div>
            <div style='color:{text_color};font-size:13px;line-height:1.6;'>{action_text}</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("## Understanding Your Fans")
        st.markdown("Five signals driving fan behavior right now")
        st.markdown(f"<span style='font-size:12px;color:{SUBTEXT};'>Click any signal → see drill-down with posts, affected segments, thematic breakdown, and recommended action.</span>", unsafe_allow_html=True)
        st.markdown("")

        signals = generate_mock_signals()
        all_signals = ["loyalty_stress", "identity_anchor", "conversion_moment", "cross_sport_superfan", "trust_split"]

        for signal_key in all_signals:
            sig = signals[signal_key]

            col1, col2, col3, col4, col5 = st.columns([2, 0.8, 1, 1, 0.5])

            with col1:
                st.markdown(f"<div style='font-weight:700;color:{TEXT};font-size:15px;'>{sig['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<span style='font-size:12px;color:{SUBTEXT};'>{sig['description']}</span>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"<div class='metric-value'>{sig['metric']}</div>", unsafe_allow_html=True)

            with col3:
                st.markdown(f"<div style='font-size:12px;color:{SUBTEXT};font-weight:500;'>Trend</div>", unsafe_allow_html=True)
                st.markdown(f"<span class='{sig['trend_class']}' style='font-size:16px;font-weight:700;'>{sig['trend']}</span>", unsafe_allow_html=True)

            with col4:
                st.markdown(f"<div style='font-size:12px;color:{SUBTEXT};font-weight:500;'>Status</div>", unsafe_allow_html=True)
                st.markdown(f"<span class='status-badge {sig['status_class']}'>{sig['status']}</span>", unsafe_allow_html=True)

            with col5:
                if st.button("→", key=f"drill_{signal_key}", help="View detailed analysis"):
                    st.session_state["drill_down_signal"] = signal_key
                    st.rerun()

            st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state["current_page"] == "Segments":

    if st.session_state["viewing_segment"]:
        segment_name = st.session_state["viewing_segment"]
        seg_data = generate_segment_thematic_data(segment_name)

        col_back, col_title = st.columns([1, 3])
        with col_back:
            if st.button("← Back to Segments", use_container_width=True):
                st.session_state["viewing_segment"] = None
                st.rerun()

        with col_title:
            st.markdown(f"<h2 style='margin:0;color:{TEXT};'>{segment_name}</h2>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("")

        st.markdown("### Segment Overview")
        sum_col1, sum_col2, sum_col3 = st.columns(3)

        with sum_col1:
            st.metric("Total Fans", seg_data.get("count", 0), border=False)

        with sum_col2:
            st.metric("Percentage", f"{seg_data.get('pct', 0)}%", border=False)

        with sum_col3:
            st.markdown(f"<div style='font-size:12px;color:{SUBTEXT};font-weight:600;margin-bottom:8px;'>DESCRIPTION</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:13px;color:{TEXT};'>{seg_data.get('description', '')}</div>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("---")
        st.markdown("")

        st.markdown("### Why These Fans Became Fans")
        st.markdown(f"<span style='font-size:12px;color:{SUBTEXT};'>Updated monthly to track composition shifts</span>", unsafe_allow_html=True)

        thematic = seg_data.get("thematic", {})
        if thematic:
            sorted_thematic = sorted(thematic.items(), key=lambda x: x[1], reverse=True)
            for reason, pct in sorted_thematic:
                col_label, col_bar, col_pct = st.columns([2.5, 3, 0.5])
                with col_label:
                    st.markdown(f"<span style='font-size:13px;color:{TEXT};'>{reason}</span>", unsafe_allow_html=True)
                with col_bar:
                    st.progress(int(pct) / 100)
                with col_pct:
                    st.markdown(f"<span style='font-size:13px;font-weight:600;color:{PRIMARY};'>{pct}%</span>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("---")
        st.markdown("")

        st.markdown("### What They Care About Right Now")
        st.markdown(f"<span style='font-size:12px;color:{SUBTEXT};'>Current priorities shaping engagement decisions</span>", unsafe_allow_html=True)

        cares_about = seg_data.get("what_they_care_about", {})
        if cares_about:
            sorted_cares = sorted(cares_about.items(), key=lambda x: x[1], reverse=True)
            for topic, pct in sorted_cares:
                col_label, col_bar, col_pct = st.columns([2.5, 3, 0.5])
                with col_label:
                    st.markdown(f"<span style='font-size:13px;color:{TEXT};'>{topic}</span>", unsafe_allow_html=True)
                with col_bar:
                    st.progress(int(pct) / 100)
                with col_pct:
                    st.markdown(f"<span style='font-size:13px;font-weight:600;color:{PRIMARY};'>{pct}%</span>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("---")
        st.markdown("")

        st.markdown("### Sample Quotes from This Segment")
        for quote in seg_data.get("sample_quotes", []):
            st.markdown(f"""
            <div style='background:{CARD_BG};border-left:4px solid {PRIMARY};padding:16px;margin-bottom:12px;border-radius:8px;'>
                <div style='font-size:13px;color:{TEXT};font-style:italic;'>{quote}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("---")
        st.markdown("")

        risk_col, opp_col = st.columns(2)

        with risk_col:
            st.markdown("### Risk Assessment")
            risk_text = seg_data.get("risk", "")
            st.markdown(f"""
            <div style='background:#fee2e2;border-left:4px solid #dc2626;padding:16px;border-radius:8px;'>
                <div style='color:#991b1b;font-weight:700;font-size:12px;margin-bottom:8px;'>⚠️ RISK</div>
                <div style='color:#991b1b;font-size:13px;'>{risk_text}</div>
            </div>
            """, unsafe_allow_html=True)

        with opp_col:
            st.markdown("### Opportunity")
            opp_text = seg_data.get("opportunity", "")
            st.markdown(f"""
            <div style='background:#e8f5e9;border-left:4px solid {PRIMARY};padding:16px;border-radius:8px;'>
                <div style='color:#1b4d3e;font-weight:700;font-size:12px;margin-bottom:8px;'>✓ OPPORTUNITY</div>
                <div style='color:#1b4d3e;font-size:13px;'>{opp_text}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("## Fan Segments")
        st.markdown("Understanding your fan base composition and thematic drivers")
        st.markdown(f"<span style='font-size:12px;color:{SUBTEXT};'>Click any segment → view thematic breakdown (why they became fans, what they care about now), risk assessment, and engagement opportunities.</span>", unsafe_allow_html=True)
        st.markdown("")

        segments_data = {
            "Identity-Driven Advocate": {"count": 156, "pct": 28},
            "Vocal Supporter": {"count": 112, "pct": 20},
            "Observer": {"count": 98, "pct": 18},
            "Supporter": {"count": 87, "pct": 16},
            "Skeptical Observer": {"count": 65, "pct": 12},
            "Community Organizer": {"count": 34, "pct": 6},
        }

        cols = st.columns(3)
        for idx, (segment, data) in enumerate(segments_data.items()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class='signal-card'>
                    <div style='font-weight:700;color:{TEXT};margin-bottom:8px;'>{segment}</div>
                    <div style='font-size:24px;font-weight:700;color:{PRIMARY};'>{data['count']}</div>
                    <div style='font-size:12px;color:{SUBTEXT};margin-top:4px;'>{data['pct']}% of fanbase</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("View Thematic Breakdown →", key=f"segment_{segment}", use_container_width=True):
                    st.session_state["viewing_segment"] = segment
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CULTURAL FEED (LAYER 3)
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state["current_page"] == "Cultural Feed":
    st.markdown("## Cultural Signal Feed")
    st.markdown("Non-sports events influencing fan behavior")
    st.markdown(f"<span style='font-size:12px;color:{SUBTEXT};'>What's pulling fans in or pushing them away outside the game itself. Real-time cultural context.</span>", unsafe_allow_html=True)
    st.markdown("")

    feed_items = [
        ("Women's History Month campaign trending", "Positive sentiment +18%", "Apr 13"),
        ("Social justice movements gaining attention", "Positive sentiment +12%", "Apr 12"),
        ("Team leadership updates", "Neutral +5%", "Apr 11"),
        ("Player mental health advocacy goes viral", "Positive sentiment +24%", "Apr 10"),
    ]

    for event, sentiment, date in feed_items:
        sent_color = "#16a34a" if "Positive" in sentiment else "#dc2626" if "Negative" in sentiment else "#6b7280"
        st.markdown(f"""
        <div style='background:{CARD_BG};padding:12px;border-radius:8px;margin-bottom:8px;border-left:4px solid {sent_color};'>
            <div style='font-weight:600;color:{TEXT};'>{event}</div>
            <div style='font-size:12px;color:{SUBTEXT};margin-top:4px;'>{sentiment} · {date}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: INSIGHTS (LAYER 3)
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state["current_page"] == "Insights":
    st.markdown("## Insights & Analysis")
    st.markdown(f"<span style='font-size:12px;color:{SUBTEXT};'>Advanced tools: 24-hour summaries, signal patterns, outcome projections.</span>", unsafe_allow_html=True)

    insight_tabs = st.tabs(["Daily Pulse", "Pattern Map", "Simulation"])

    with insight_tabs[0]:
        st.markdown("### Daily Pulse — Last 24 Hours")
        st.markdown(f"<span style='color:{SUBTEXT};font-size:12px;'>Ready to forward. No jargon.</span>", unsafe_allow_html=True)

        # Daily Pulse using native Streamlit components
        st.markdown("#### 🔴 LOYALTY RISK — 18% (+2% from yesterday)")
        st.markdown("Growing disengagement signals across community. 8 new mentions of player departure concerns in past 24 hours. **Window for intervention: 7-14 days** before churn becomes visible in ticket data.")

        st.markdown("#### 🟢 CONVERSION WINDOW — 12 new fans")
        st.markdown("Stable conversion rate. Player storytelling content performing at baseline. **Opportunity is open**; no immediate action needed but maintain current content strategy.")

        st.markdown("#### 🟡 TRUST GAP — Widening (+3 pts)")
        st.markdown("Player sentiment remains strong (+72%). Institutional sentiment declining (+18%). Two governance posts went viral; 145 comments expressing skepticism. **Early warning signal** for sponsorship and brand risk if gap continues to widen.")

        st.markdown("#### ✓ CULTURAL SIGNAL — Women's empowerment trending")
        st.markdown("34 posts yesterday about social causes and women's rights. Positive sentiment. **Opportunity to align** organizational messaging with this moment.")

        st.divider()
        st.caption("📊 Last updated: 6:02 AM ET — Forward this to stakeholders")

    with insight_tabs[1]:
        st.markdown("### Pattern Map — Signal Clusters")
        st.markdown("How posts and signals group across themes, emotions, and behavioral pathways")

        data = {
            "x": [1, 2, 3, 4, 5, 2, 3, 4, 1, 5],
            "y": [2, 3, 1, 4, 5, 4, 2, 3, 5, 1],
            "segment": ["Identity-Driven", "Vocal Supporter", "Observer", "Detractor", "Supporter",
                       "Identity-Driven", "Detractor", "Supporter", "Observer", "Vocal Supporter"],
            "size": [15, 12, 8, 10, 18, 14, 9, 16, 7, 20],
        }

        fig = px.scatter(
            data,
            x="x",
            y="y",
            color="segment",
            size="size",
            title="PCA of Signal Clusters",
            labels={"x": "Engagement Level →", "y": "Sentiment Polarity →"},
        )
        fig.update_traces(marker=dict(line=dict(width=1, color="white")))
        st.plotly_chart(fig, use_container_width=True)

    with insight_tabs[2]:
        st.markdown("### Simulation — Action vs Status Quo")
        st.markdown("What happens if we act on the Loyalty Stress signal?")

        sim_col1, sim_col2 = st.columns(2)

        with sim_col1:
            st.markdown("#### Status Quo (Do Nothing)")
            st.metric("At-risk fans remaining", "18%", "+3%")
            st.metric("30-day churn risk", "8.2%", "—")
            st.metric("Bottom-tier fans", "34%", "+2%")

        with sim_col2:
            st.markdown("#### With Recommended Action")
            st.metric("At-risk fans converted", "62%", "-6%")
            st.metric("30-day churn risk", "2.8%", "-5.4pp")
            st.metric("Core fan retention", "87%", "+4%")

        st.markdown(f"""
        <div style='background:#e8f5e9;border-left:4px solid #16a34a;padding:16px;border-radius:8px;margin-top:20px;'>
            <h4 style='color:#2e7d32;margin-top:0;'>Recommended Action: Community Re-engagement Campaign</h4>
            <ul style='color:#2e7d32;'>
                <li>Timeline: Launch within 7 days</li>
                <li>Target: 18% at-risk loyalists</li>
                <li>Expected outcome: 62% conversion back to core fans</li>
                <li>Risk: Delay beyond 14 days reduces effectiveness</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("FanVerse Dashboard — Mock Data for Design Validation")
