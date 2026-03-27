# seed_mock_data.py
# Populates the repository with realistic fake data for development and demos.
# Run this file directly: python seed_mock_data.py
#
# When real scrapers are ready, they call ingest() with their own data.
# This file stays as-is — both sources live in the same repository.

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ingest import ingest, repo_stats

MOCK_ENTRIES = [

    # WASSERMAN
    {
        "text": "Female sports fans are not a monolith. Our research identifies six distinct segments ranging from identity-driven superfans to casual cultural observers, each requiring a different engagement strategy.",
        "source": "wasserman",
        "report_title": "Wasserman Women's Sports Study 2024",
        "url": "https://www.teamwass.com/news/the-shareable-2024/",
        "sports": ["general"],
        "date": "2024-02-01",
        "season_phase": "unknown",
    },
    {
        "text": "WNBA female fans are 34% more likely than male fans to say their fandom is tied to a specific player rather than a team, indicating that player-driven marketing outperforms team-centric campaigns for this segment.",
        "source": "wasserman",
        "report_title": "Wasserman Women's Sports Study 2024",
        "url": "https://www.teamwass.com/news/the-shareable-2024/",
        "sports": ["WNBA"],
        "date": "2024-02-01",
        "season_phase": "unknown",
    },
    {
        "text": "Social media is the primary discovery channel for new female fans, with 61% of women under 35 citing Instagram or TikTok as the platform where they first engaged with a women's sports league.",
        "source": "wasserman",
        "report_title": "Wasserman Women's Sports Study 2024",
        "url": "https://www.teamwass.com/news/the-shareable-2024/",
        "sports": ["general"],
        "date": "2024-02-01",
        "season_phase": "unknown",
    },

    # DELOITTE
    {
        "text": "Women's sports viewership grew 23% year-over-year in 2023, driven largely by increased media rights investment and the visibility boost from multi-sport athletes who cross over between leagues.",
        "source": "deloitte",
        "report_title": "Deloitte Sports Business Group: Women's Sports Report 2024",
        "url": "https://www.deloitte.com/global/en/Industries/tmt/analysis/women-sports.html",
        "sports": ["general"],
        "date": "2024-01-15",
        "season_phase": "unknown",
    },
    {
        "text": "Female fans of the NWSL show a 2.4x higher merchandise purchase rate when a player they follow publicly advocates for a social cause aligned with the fan's personal values.",
        "source": "deloitte",
        "report_title": "Deloitte Sports Business Group: Women's Sports Report 2024",
        "url": "https://www.deloitte.com/global/en/Industries/tmt/analysis/women-sports.html",
        "sports": ["NWSL"],
        "date": "2024-01-15",
        "season_phase": "unknown",
    },
    {
        "text": "Sponsorship recall among female fans increases significantly when brand messaging is integrated into player storytelling rather than traditional broadcast placements — a 47% higher recall rate was observed in test markets.",
        "source": "deloitte",
        "report_title": "Deloitte Sports Business Group: Women's Sports Report 2024",
        "url": "https://www.deloitte.com/global/en/Industries/tmt/analysis/women-sports.html",
        "sports": ["general"],
        "date": "2024-01-15",
        "season_phase": "unknown",
    },

    # BCG
    {
        "text": "The female sports fan base represents a $1.3 trillion opportunity that most brands are systematically underinvesting in, treating women's sports as a CSR play rather than a commercial growth driver.",
        "source": "bcg",
        "report_title": "BCG: It's Game Time — The Rise of Women's Sports Fans",
        "url": "https://www.bcg.com/publications/2023/the-rise-of-women-sports-fans",
        "sports": ["general"],
        "date": "2023-11-01",
        "season_phase": "unknown",
    },
    {
        "text": "Cross-sport female fans — those who actively follow two or more women's leagues — represent only 18% of the female fan base but account for 41% of total fan spending across tickets, merchandise, and streaming.",
        "source": "bcg",
        "report_title": "BCG: It's Game Time — The Rise of Women's Sports Fans",
        "url": "https://www.bcg.com/publications/2023/the-rise-of-women-sports-fans",
        "sports": ["WNBA", "NWSL", "WTA"],
        "date": "2023-11-01",
        "season_phase": "unknown",
    },
    {
        "text": "WTA fans show the highest median household income of any women's sports fandom segment at $94,000, making tennis disproportionately attractive for premium brand partnerships.",
        "source": "bcg",
        "report_title": "BCG: It's Game Time — The Rise of Women's Sports Fans",
        "url": "https://www.bcg.com/publications/2023/the-rise-of-women-sports-fans",
        "sports": ["WTA"],
        "date": "2023-11-01",
        "season_phase": "unknown",
    },

    # NIELSEN
    {
        "text": "84% of female sports fans say they feel underrepresented by sports media coverage, with only 15% of sports media airtime dedicated to women's leagues despite growing viewership numbers.",
        "source": "nielsen",
        "report_title": "Nielsen Fan Insights: Women's Sports 2024",
        "url": "https://www.nielsen.com/insights/2024/womens-sports/",
        "sports": ["general"],
        "date": "2024-03-01",
        "season_phase": "preseason",
        "week": 1,
    },
    {
        "text": "WNBA playoff viewership among women 18-34 increased 58% in 2023, the highest single-season growth rate of any professional sports league in that demographic.",
        "source": "nielsen",
        "report_title": "Nielsen Fan Insights: Women's Sports 2024",
        "url": "https://www.nielsen.com/insights/2024/womens-sports/",
        "sports": ["WNBA"],
        "date": "2024-03-01",
        "season_phase": "playoff",
    },
    {
        "text": "Female fans demonstrate stronger brand loyalty transfer than male fans: when a preferred athlete endorses a product, 67% of female fans report a sustained positive brand perception versus 43% for male fans.",
        "source": "nielsen",
        "report_title": "Nielsen Fan Insights: Women's Sports 2024",
        "url": "https://www.nielsen.com/insights/2024/womens-sports/",
        "sports": ["general"],
        "date": "2024-03-01",
        "season_phase": "unknown",
    },

    # MCKINSEY
    {
        "text": "Organizations that invest in community-building infrastructure for female fans — dedicated forums, fan councils, player access programs — see a 31% improvement in season ticket renewal rates over a 3-year period.",
        "source": "mckinsey",
        "report_title": "McKinsey: Winning the Female Sports Fan",
        "url": "https://www.mckinsey.com/industries/sports/our-insights/winning-the-female-fan",
        "sports": ["general"],
        "date": "2024-02-15",
        "season_phase": "unknown",
    },
    {
        "text": "Disengagement among female WNBA fans typically follows a predictable pattern: reduced social media engagement precedes ticket purchase decline by 4-6 weeks, offering a measurable early warning signal for retention teams.",
        "source": "mckinsey",
        "report_title": "McKinsey: Winning the Female Sports Fan",
        "url": "https://www.mckinsey.com/industries/sports/our-insights/winning-the-female-fan",
        "sports": ["WNBA"],
        "date": "2024-02-15",
        "season_phase": "midseason",
        "week": 8,
    },
    {
        "text": "Female volleyball fans represent the fastest-growing segment in women's sports, with a 44% year-over-year increase in self-identified fandom driven by NCAA tournament exposure and a surge in professional league visibility.",
        "source": "mckinsey",
        "report_title": "McKinsey: Winning the Female Sports Fan",
        "url": "https://www.mckinsey.com/industries/sports/our-insights/winning-the-female-fan",
        "sports": ["volleyball"],
        "date": "2024-02-15",
        "season_phase": "unknown",
    },
]

if __name__ == "__main__":
    print("Seeding FanVerse repository with mock data...\n")
    result = ingest(MOCK_ENTRIES)
    print(f"\nDone. {result['added']} records added, {result['skipped_duplicates']} skipped.")
    print("\nRepository stats:")
    repo_stats()