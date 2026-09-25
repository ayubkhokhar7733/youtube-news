#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
core/news_scraper.py — Live Trending News Scraper with Anti-Collision & Deduplication.

Features:
- Slices real-time news from Google News RSS and top Reddit communities.
- Extracts clean headlines, verified source publications, summaries, and timestamps.
- Checks data/news_history.json using string similarity to prevent repeating stories.
- Produces a rich Story Dossier with key facts, sources, and context for the scriptwriter.
"""

import os
import sys
import json
import time
import re
import difflib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter

import config

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
NEWS_HISTORY_FILE = os.path.join(DATA_DIR, "news_history.json")
os.makedirs(DATA_DIR, exist_ok=True)

# Session with robust browser headers and connection pooling
_session = requests.Session()
_adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=2)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)
_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
})

CATEGORY_QUERIES = {
    "ai": [
        "Artificial Intelligence OR OpenAI OR Anthropic OR DeepSeek OR Nvidia AI when:1d",
        "Generative AI OR ChatGPT OR Claude 3.5 OR AI robotics when:1d",
    ],
    "trump": [
        "Donald Trump OR Trump administration OR White House announcement when:1d",
        "Donald Trump executive order OR press conference OR policy when:1d",
    ],
    "tech": [
        "technology breaking news OR Apple OR Microsoft OR Tesla OR Elon Musk when:1d",
        "major tech announcement OR cyber security OR space tech when:1d",
    ],
    "global": [
        "breaking world news OR international diplomacy OR global summit when:1d",
        "major global economy OR geopolitical event when:1d",
    ],
}

REDDIT_SUBREDDITS = {
    "ai": ["singularity", "artificial"],
    "trump": ["news", "politics"],
    "tech": ["technology", "gadgets"],
    "global": ["worldnews", "news"],
}


# ---------------------------------------------------------------------------
# History & Anti-Collision Management
# ---------------------------------------------------------------------------

def load_news_history() -> list:
    """Load previously processed news stories from JSON history."""
    if os.path.exists(NEWS_HISTORY_FILE):
        try:
            with open(NEWS_HISTORY_FILE, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("history", [])
        except Exception as e:
            print(f"[news_scraper] Error loading history: {e}")
    return []


def save_news_history(history: list):
    """Save processed news history to JSON file."""
    with open(NEWS_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"history": history}, f, indent=2, ensure_ascii=False)


def record_story_in_history(story: dict):
    """Append newly selected story to history to prevent future duplicates."""
    history = load_news_history()
    entry = {
        "title": story.get("title", ""),
        "source": story.get("source", ""),
        "category": story.get("category", ""),
        "url": story.get("url", ""),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    history.append(entry)
    # Keep last 500 entries (rolling window)
    if len(history) > 500:
        history = history[-500:]
    save_news_history(history)


def is_story_duplicate(candidate_title: str, history: list, threshold: float = 0.60) -> bool:
    """Check if candidate headline is too similar to any story covered recently (past 14 days)."""
    clean_candidate = re.sub(r'[^a-zA-Z0-9 ]', '', candidate_title).lower().strip()
    candidate_tokens = set(clean_candidate.split())

    for entry in reversed(history[-150:]):
        past_title = entry.get("title", "")
        clean_past = re.sub(r'[^a-zA-Z0-9 ]', '', past_title).lower().strip()
        past_tokens = set(clean_past.split())

        # Sequence matcher ratio
        seq_ratio = difflib.SequenceMatcher(None, clean_candidate, clean_past).ratio()
        if seq_ratio >= threshold:
            return True

        # Jaccard token overlap for word combinations
        if candidate_tokens and past_tokens:
            jaccard = len(candidate_tokens & past_tokens) / len(candidate_tokens | past_tokens)
            if jaccard >= 0.55:
                return True

    return False


# ---------------------------------------------------------------------------
# Scraping: Google News RSS
# ---------------------------------------------------------------------------

def _clean_html_text(raw_html: str) -> str:
    """Strip HTML tags and clean up whitespace."""
    if not raw_html:
        return ""
    text = re.sub(r'<[^>]+>', ' ', raw_html)
    text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def scrape_google_news_rss(query: str, max_items: int = 15) -> list:
    """
    Fetch trending news articles from Google News RSS for a query.
    Returns list of dicts: title, source, url, pub_date, summary.
    """
    encoded_query = requests.utils.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    stories = []
    try:
        resp = _session.get(rss_url, timeout=12)
        if resp.status_code != 200:
            print(f"[news_scraper] Google News RSS returned HTTP {resp.status_code}")
            return []

        root = ET.fromstring(resp.content)
        items = root.findall(".//item")

        for item in items[:max_items]:
            raw_title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            desc_el = item.find("description")
            raw_desc = desc_el.text if desc_el is not None else ""

            # Parse "Headline - Source Name"
            source = "News Source"
            title = raw_title
            if " - " in raw_title:
                parts = raw_title.rsplit(" - ", 1)
                title = parts[0].strip()
                source = parts[1].strip()

            summary = _clean_html_text(raw_desc)
            if summary.startswith(raw_title):
                summary = summary[len(raw_title):].strip()

            if title and len(title) > 15:
                stories.append({
                    "title": title,
                    "source": source,
                    "url": link,
                    "pub_date": pub_date,
                    "summary": summary,
                    "provider": "Google News",
                })
    except Exception as e:
        print(f"[news_scraper] Error fetching Google News RSS: {e}")

    return stories


# ---------------------------------------------------------------------------
# Scraping: Reddit Trending Tech/News (Zero API Key)
# ---------------------------------------------------------------------------

def scrape_reddit_trending(subreddit: str, max_items: int = 10) -> list:
    """Fetch top trending discussion topics from Reddit JSON endpoint."""
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t=day&limit={max_items}"
    stories = []
    try:
        resp = _session.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            children = data.get("data", {}).get("children", [])
            for child in children:
                pdata = child.get("data", {})
                title = pdata.get("title", "").strip()
                score = pdata.get("score", 0)
                permalink = f"https://reddit.com{pdata.get('permalink', '')}"
                selftext = pdata.get("selftext", "")[:400].strip()

                if title and score > 20:
                    stories.append({
                        "title": title,
                        "source": f"r/{subreddit}",
                        "url": permalink,
                        "pub_date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        "summary": selftext or f"Trending community discussion with {score}+ upvotes.",
                        "provider": "Reddit",
                        "score": score,
                    })
    except Exception as e:
        print(f"[news_scraper] Reddit fetch failed for r/{subreddit}: {e}")
    return stories


# ---------------------------------------------------------------------------
# High-Level News Aggregator & Story Dossier Builder
# ---------------------------------------------------------------------------

def get_trending_story(category: str = "ai", query_override: str = None) -> dict:
    """
    Pulls real-time news candidates, filters against collision history,
    and returns a clean Story Dossier ready for scriptwriting.
    """
    category = category.lower()
    if category not in CATEGORY_QUERIES:
        category = "ai"

    history = load_news_history()
    candidates = []

    if query_override:
        print(f"[news_scraper] Searching for custom query: '{query_override}'")
        candidates = scrape_google_news_rss(query_override, max_items=20)
    else:
        print(f"[news_scraper] Sourcing breaking news for category: '{category.upper()}'...")
        queries = CATEGORY_QUERIES.get(category, CATEGORY_QUERIES["ai"])
        for q in queries:
            fetched = scrape_google_news_rss(q, max_items=15)
            candidates.extend(fetched)

        # Also pull top discussions from relevant subreddits
        subs = REDDIT_SUBREDDITS.get(category, [])
        for sub in subs:
            r_fetched = scrape_reddit_trending(sub, max_items=5)
            candidates.extend(r_fetched)

    if not candidates:
        raise RuntimeError(f"Could not source any news items for category '{category}'. Check internet connection.")

    # Filter out duplicates and past coverage
    fresh_candidates = []
    for cand in candidates:
        if not is_story_duplicate(cand["title"], history):
            fresh_candidates.append(cand)

    if not fresh_candidates:
        print("[news_scraper] All candidates were recently covered in history. Picking least recent fresh item...")
        fresh_candidates = candidates

    selected = fresh_candidates[0]

    # Assemble Story Dossier
    related_summaries = [c["title"] for c in fresh_candidates[1:5]]
    dossier = {
        "title": selected["title"],
        "primary_source": selected["source"],
        "url": selected["url"],
        "pub_date": selected["pub_date"],
        "summary": selected["summary"],
        "category": category,
        "related_angles": related_summaries,
        "raw_candidate_count": len(candidates),
    }

    print(f"[news_scraper] Selected Story: '{dossier['title']}' (Source: {dossier['primary_source']})")
    return dossier


if __name__ == "__main__":
    test_cat = sys.argv[1] if len(sys.argv) > 1 else "ai"
    print(f"Testing News Scraper on category: {test_cat}")
    res = get_trending_story(category=test_cat)
    print("\n--- STORY DOSSIER ---")
    print(json.dumps(res, indent=2))
