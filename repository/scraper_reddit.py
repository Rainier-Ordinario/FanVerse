# scraper_reddit.py
# Scrapes Reddit for female fan conversations across sports subreddits.
# Uses Reddit's public .json endpoints — no API key or app registration required.
# Feeds results into ingest() in ingest.py.
#
# Usage:
#   cd repository/
#   python scraper_reddit.py
#
# Install dependencies: pip install requests python-dotenv

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from ingest import ingest  # noqa: E402

load_dotenv(Path(__file__).parent / ".env", override=False)

# Reddit requires a descriptive User-Agent — vague agents get throttled or blocked.
# Set REDDIT_USER_AGENT in .env to customize (see .env.example).
USER_AGENT = os.environ.get(
    "REDDIT_USER_AGENT",
    "script:FanVerse-scraper:v0.1 (research project)"
)

BASE_URL = "https://www.reddit.com"

# Conservative delay between requests for unauthenticated access.
# Reddit's unauthenticated limit isn't published, so we play it safe.
REQUEST_DELAY = 1.0  # seconds

POST_LIMIT = 25      # hot posts to pull per subreddit
COMMENT_LIMIT = 5    # top-level comments to check per post
MIN_TEXT_LENGTH = 150  # ignore posts/comments shorter than this

# Subreddit config 

# Women's sports subreddits: the community itself signals female fandom.
# We collect all substantial posts and comments — no identity-phrase filter.
WOMENS_SUBREDDITS = {
    "wnba":              ["WNBA"],
    "NWSL":              ["NWSL"],
    "WomensSoccer":      ["general"],    # global women's football, not just NWSL
    "WTAtennis":         ["WTA"],        # dedicated WTA community
    "ProVolleyball":     ["volleyball"],
    "PWHL":              ["general"],    # women's hockey — strong identity/belonging language
    "CanadianWomensNT":  ["general"],    # passionate national team fan community
    "TwoXSports":        ["general"],    # women discussing sports as fans — very high signal
    "WomenSportsFirst":  ["general"],    # female sports fans across all sports
}

# General sports subreddits: searched by female fan signal queries instead of
# scanning hot posts, which rarely surface this language in titles/bodies.
SEARCH_SUBREDDITS = {
    "nba":      ["general"],
    "soccer":   ["general"],
    "tennis":   ["general"],
    "baseball": ["general"],
    "nfl":      ["general"],
}

SEARCH_QUERIES = [
    "female fan",
    "women fans",
    "as a woman fan",
    "girl fan",
]

# Female fan signal detection
FEMALE_FAN_SIGNALS = [
    # Explicit identity statements
    "as a woman", "as a female", "as a girl",
    "i'm a woman", "i am a woman", "im a woman",
    "i'm a girl", "i am a girl", "im a girl",
    "as a woman fan", "as a female fan", "as a girl who",
    "woman who watches", "girl who watches",
    # Community references
    "women fans", "female fans", "female fan",
    "women who watch", "women who follow",
    "lady fans", "girl fans",
    "female fandom", "women's fandom",
    "female sports fan", "women sports fan",
    "women's sports fan", "female sports fans",
    # Lived experience framing
    "being a woman", "being female", "being a girl",
    "as a female sports", "as a woman sports",
    "experience as a woman", "experience as a female",
    # First-person identity claims
    "she/her", "woman here", "girl here", "female here",
    # Conversion moments (Insight 3)
    "got me into", "got me hooked", "first game i ever",
    "that's what got me", "fell in love with", "changed everything for me",
    "i became a fan when", "i became a fan after",
    "never watched before", "didn't watch until",
    # Loyalty and identity anchors (Insights 1 & 2)
    "she's the reason", "she's why i", "she got me",
    "my favorite player", "i've been a fan since", "grew up watching",
    "been following since", "been a fan for years",
    "loyalty", "will always support", "stick with",
    # Disengagement signals (Insight 1)
    "can't watch anymore", "stopped watching", "lost me as a fan",
    "done with", "i gave up on", "used to love",
    "not the same anymore", "hard to keep supporting",
    # Trust and institution vs player split (Insight 5)
    "love the player hate the", "still support her even",
    "the league let", "the organization failed",
    "front office", "ownership doesn't care",
    # Cross-sport super fan (Insight 4)
    "also follow", "watch both", "big fan of both",
    "wnba and", "nwsl and", "women's soccer and",
]


MOD_PHRASES = [
    "mod post", "moderator", "weekly thread", "free talk", "megathread",
    "match thread", "game thread", "daily thread", "weekly discussion",
    "jobs", "listings", "broadcast details", "pinned", "[mod]",
    "auto-generated", "bot",
    # Gear/sizing questions — not fandom signal
    "unisex kit", "kit sizing", "3xl",
    # Collectibles spam
    "panini", "trading card",
    # Stream-finding posts
    "vod", "streaming link",
]


def is_mod_post(title: str, body: str) -> bool:
    if len(title) < 15:
        return True
    combined = (title + " " + body).lower()
    return any(phrase in combined for phrase in MOD_PHRASES)


def is_english(text: str) -> bool:
    if not text:
        return False
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    return ascii_chars / len(text) >= 0.85


def is_url_only(text: str) -> bool:
    import re
    cleaned = re.sub(r'http\S+', '', text).strip()
    return len(cleaned) < MIN_TEXT_LENGTH


def has_female_fan_signal(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in FEMALE_FAN_SIGNALS)


# Season phase inference
def infer_season_phase(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["finals", "championship", "title game"]):
        return "finals"
    if any(w in lower for w in ["playoff", "playoffs", "postseason", "bracket"]):
        return "playoff"
    if any(w in lower for w in ["preseason", "pre-season", "training camp", "draft"]):
        return "preseason"
    if any(w in lower for w in ["offseason", "off-season", "free agency", "trade deadline"]):
        return "offseason"
    if any(w in lower for w in ["all-star", "all star", "midseason", "mid-season"]):
        return "midseason"
    return "unknown"


# HTTP helpers
def ts_to_date(utc_timestamp: float) -> str:
    return datetime.fromtimestamp(utc_timestamp, tz=timezone.utc).strftime("%Y-%m-%d")


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def reddit_get(session: requests.Session, url: str, params: dict = None) -> Optional[dict]:
    """GET a Reddit .json endpoint. Handles rate limits and transient errors."""
    for attempt in range(3):
        try:
            resp = session.get(url, params=params, timeout=15)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 60))
                print(f"  Rate limited — waiting {wait}s before retry...")
                time.sleep(wait)
                continue
            if resp.status_code == 404:
                print(f"  404 — subreddit not found or private: {url}")
                return None
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            if attempt == 2:
                print(f"  Request failed after 3 attempts: {exc}")
                return None
            time.sleep(5)
    return None

# Search for subreddit with female fan 
def search_subreddit(
    session: requests.Session,
    subreddit_name: str,
    sports: list[str],
) -> list[dict]:
    """
    Search a subreddit for each female fan signal query and collect matching
    posts and their top comments. All existing quality filters apply.
    """
    entries = []
    seen_post_ids = set()
    collected_posts = 0
    collected_comments = 0

    for query in SEARCH_QUERIES:
        url = f"{BASE_URL}/r/{subreddit_name}/search.json"
        data = reddit_get(session, url, params={
            "q": query,
            "sort": "relevance",
            "limit": 25,
            "restrict_sr": 1,
        })
        time.sleep(REQUEST_DELAY)
        if not data:
            continue

        posts = [
            child["data"]
            for child in data["data"]["children"]
            if child["kind"] == "t3"
        ]

        for post in posts:
            post_id = post["id"]
            if post_id in seen_post_ids:
                continue
            seen_post_ids.add(post_id)

            post_body = post.get("selftext", "").strip()
            post_title = post.get("title", "").strip()
            post_text = f"{post_title}\n\n{post_body}".strip()
            post_date = ts_to_date(post["created_utc"])
            post_url = f"https://www.reddit.com{post['permalink']}"
            report_title = f"r/{subreddit_name}: {post_title[:120]}"

            # Apply quality filters — signal already guaranteed by search query
            post_passes = (
                post.get("is_self")
                and len(post_body) >= MIN_TEXT_LENGTH
                and post.get("score", 0) >= 2
                and not post.get("stickied", False)
                and not is_mod_post(post_title, post_body)
                and is_english(post_text)
                and not is_url_only(post_text)
            )

            if post_passes:
                entries.append({
                    "text": post_text[:3000],
                    "source": "reddit",
                    "report_title": report_title,
                    "url": post_url,
                    "sports": sports,
                    "record_date": post_date,
                    "season_phase": infer_season_phase(post_text),
                    "extra": {
                        "subreddit": subreddit_name,
                        "reddit_post_id": post_id,
                        "content_type": "post",
                        "score": post.get("score", 0),
                        "search_query": query,
                    },
                })
                collected_posts += 1
                print(f"  [post] {post_title[:70]}")

            comments = fetch_comments(session, subreddit_name, post_id)
            for comment in comments:
                body = comment.get("body", "").strip()
                if not body or body in ("[deleted]", "[removed]"):
                    continue
                if len(body) < MIN_TEXT_LENGTH:
                    continue
                if not is_english(body):
                    continue
                if is_url_only(body):
                    continue
                if not has_female_fan_signal(body):
                    continue

                comment_date = ts_to_date(comment["created_utc"])
                comment_url = f"https://www.reddit.com{comment['permalink']}"
                entries.append({
                    "text": body[:2000],
                    "source": "reddit",
                    "report_title": report_title,
                    "url": comment_url,
                    "sports": sports,
                    "record_date": comment_date,
                    "season_phase": infer_season_phase(body),
                    "extra": {
                        "subreddit": subreddit_name,
                        "reddit_post_id": post_id,
                        "reddit_comment_id": comment["id"],
                        "content_type": "comment",
                        "score": comment.get("score", 0),
                        "search_query": query,
                    },
                })
                collected_comments += 1

    print(
        f"  → {len(seen_post_ids)} posts scanned | "
        f"{collected_posts} posts + {collected_comments} comments kept"
    )
    return entries


def fetch_posts(session: requests.Session, subreddit_name: str) -> list[dict]:
    url = f"{BASE_URL}/r/{subreddit_name}/hot.json"
    data = reddit_get(session, url, params={"limit": POST_LIMIT})
    time.sleep(REQUEST_DELAY)
    if not data:
        return []
    return [
        child["data"]
        for child in data["data"]["children"]
        if child["kind"] == "t3"  # t3 = post/link
    ]


def fetch_comments(session: requests.Session, subreddit_name: str, post_id: str) -> list[dict]:
    url = f"{BASE_URL}/r/{subreddit_name}/comments/{post_id}.json"
    data = reddit_get(session, url, params={"limit": COMMENT_LIMIT, "depth": 1})
    time.sleep(REQUEST_DELAY)
    if not data or len(data) < 2:
        return []
    # Response is [post_listing, comment_listing]. We want index 1.
    return [
        child["data"]
        for child in data[1]["data"]["children"]
        if child["kind"] == "t1"  # t1 = comment
    ]


# Core scraping
def scrape_subreddit(
    session: requests.Session,
    subreddit_name: str,
    sports: list[str],
    require_signal: bool,
) -> list[dict]:
    """
    Pull hot posts and top-level comments from one subreddit.

    require_signal=False  →  women's subreddits: collect all substantial content
    require_signal=True   →  general subreddits: only content with female-fan phrases
    """
    entries = []
    label = "signal filter" if require_signal else "broad"
    print(f"\n[r/{subreddit_name}] Fetching up to {POST_LIMIT} hot posts ({label})...")

    posts = fetch_posts(session, subreddit_name)
    if not posts:
        return entries

    collected_posts = 0
    collected_comments = 0
    rejected = {
        "not_text_post": 0,
        "stickied": 0,
        "mod_post": 0,
        "too_short": 0,
        "low_score": 0,
        "non_english": 0,
        "no_signal": 0,
    }

    for post in posts:
        post_body = post.get("selftext", "").strip()
        post_title = post.get("title", "").strip()
        post_text = f"{post_title}\n\n{post_body}".strip()
        post_date = ts_to_date(post["created_utc"])
        post_url = f"https://www.reddit.com{post['permalink']}"
        report_title = f"r/{subreddit_name}: {post_title[:120]}"
        post_id = post["id"]

        # Evaluate each filter in order and record the first failure
        post_passes = False
        if not post.get("is_self") or not post_body:
            rejected["not_text_post"] += 1
        elif post.get("stickied", False):
            rejected["stickied"] += 1
        elif is_mod_post(post_title, post_body):
            rejected["mod_post"] += 1
        elif len(post_body) < MIN_TEXT_LENGTH:
            rejected["too_short"] += 1
        elif post.get("score", 0) < 2:
            rejected["low_score"] += 1
        elif not is_english(post_text):
            rejected["non_english"] += 1
        elif is_url_only(post_text):
            rejected["too_short"] += 1
        elif require_signal and not has_female_fan_signal(post_text):
            rejected["no_signal"] += 1
        else:
            post_passes = True

        if post_passes:
            entries.append({
                "text": post_text[:3000],
                "source": "reddit",
                "report_title": report_title,
                "url": post_url,
                "sports": sports,
                "record_date": post_date,
                "season_phase": infer_season_phase(post_text),
                "extra": {
                    "subreddit": subreddit_name,
                    "reddit_post_id": post_id,
                    "content_type": "post",
                    "score": post.get("score", 0),
                },
            })
            collected_posts += 1
            print(f"  [post] {post_title[:70]}")

        # Always fetch comments — for general subs we scan all posts but only
        # save comments that pass the signal filter.
        comments = fetch_comments(session, subreddit_name, post_id)

        for comment in comments:
            body = comment.get("body", "").strip()
            if not body or body in ("[deleted]", "[removed]"):
                continue
            if len(body) < MIN_TEXT_LENGTH:
                continue
            if not is_english(body):
                continue
            if is_url_only(body):
                continue
            if require_signal and not has_female_fan_signal(body):
                continue

            comment_date = ts_to_date(comment["created_utc"])
            comment_url = f"https://www.reddit.com{comment['permalink']}"
            entries.append({
                "text": body[:2000],
                "source": "reddit",
                "report_title": report_title,
                "url": comment_url,
                "sports": sports,
                "record_date": comment_date,
                "season_phase": infer_season_phase(body),
                "extra": {
                    "subreddit": subreddit_name,
                    "reddit_post_id": post_id,
                    "reddit_comment_id": comment["id"],
                    "content_type": "comment",
                    "score": comment.get("score", 0),
                },
            })
            collected_comments += 1

    total_fetched = len(posts)
    rejection_parts = [
        f"{v} {k.replace('_', ' ')}"
        for k, v in rejected.items() if v > 0
    ]
    rejection_str = ", ".join(rejection_parts) if rejection_parts else "none"
    print(
        f"  → {total_fetched} fetched — {rejection_str} | "
        f"{collected_posts} posts + {collected_comments} comments kept"
    )
    return entries


# Main 
def main():
    print("=" * 55)
    print("  FanVerse Reddit Scraper")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 55)
    print(f"  User-Agent: {USER_AGENT}")

    session = make_session()
    all_entries = []

    print("\n── Women's Sports Subreddits (broad) ──────────────────")
    for subreddit_name, sports in WOMENS_SUBREDDITS.items():
        entries = scrape_subreddit(session, subreddit_name, sports, require_signal=False)
        all_entries.extend(entries)

    print("\n── General Subreddits (search-based, female fan queries) ──")
    for subreddit_name, sports in SEARCH_SUBREDDITS.items():
        print(f"\n[r/{subreddit_name}] Searching {len(SEARCH_QUERIES)} queries...")
        entries = search_subreddit(session, subreddit_name, sports)
        all_entries.extend(entries)

    print(f"\n── Ingesting {len(all_entries)} total entries ───────────────")
    if all_entries:
        ingest(all_entries)
    else:
        print("[Scraper] Nothing collected — Reddit may be throttling or subreddits are private.")

    print("\nDone.")


if __name__ == "__main__":
    main()
