"""Web search + fetch for official university program information.

Prioritizes official university domains (.edu, ac.uk, university name match).
Uses Tavily search API (TAVILY_API_KEY). If no key is configured or no
results are found, returns an empty list rather than fabricating content.
"""
import re
import httpx
from bs4 import BeautifulSoup
from ..config import settings
from . import robots_check

OFFICIAL_HINTS = [".edu", "ac.uk", "ac.jp", "ac.nz", "edu.au", "uni-", ".ac.", "university"]

# Third-party aggregator/ranking sites that are NOT the university itself. Their admissions info
# is frequently stale, paraphrased, or wrong, and mixing it in undermines "prioritize official
# sources" — these are excluded from fetch entirely rather than merely deprioritized.
AGGREGATOR_BLOCKLIST = [
    "gradschools.com", "niche.com", "usnews.com", "collegeconfidential.com", "prepscholar.com",
    "petersons.com", "collegesimply.com", "studyportals.com", "mastersportal.com", "topuniversities.com",
    "thegradcafe.com", "reddit.com", "quora.com", "wikipedia.org", "linkedin.com",
]

# Phrases indicating the fetched HTML is a bot-block / consent wall / JS-required shell rather
# than real page content. Only disqualifying when the page is also short — a long real page can
# legitimately mention "cookie policy" once in its footer.
BLOCK_WALL_PHRASES = [
    "enable javascript", "verify you are human", "checking your browser", "are you a robot",
    "captcha", "accept all cookies", "we use cookies to", "access denied", "403 forbidden",
    "please enable cookies", "unusual traffic", "bot detection",
]
BLOCK_WALL_MAX_LEN = 1000  # below this length, a block-wall phrase is treated as disqualifying


def _looks_official(url: str, university_name: str) -> bool:
    url_l = url.lower()
    if any(h in url_l for h in OFFICIAL_HINTS):
        return True
    tokens = [t.lower() for t in re.findall(r"[A-Za-z]+", university_name) if len(t) > 3]
    return any(t in url_l for t in tokens)


def _is_aggregator(url: str) -> bool:
    url_l = url.lower()
    return any(domain in url_l for domain in AGGREGATOR_BLOCKLIST)


def _tavily_search_raw(query: str, max_results: int = 6) -> list[dict]:
    """Shared low-level Tavily call — returns raw {url, title} results with no filtering.
    Used both for official-source search and (separately, with different domain targeting) for
    community outcome search in community_outcomes.py."""
    if not settings.tavily_api_key:
        return []
    try:
        resp = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.tavily_api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
            },
            timeout=20,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception:
        return []
    return [{"url": r["url"], "title": r.get("title", "")} for r in results if r.get("url")]


def search_program_pages(
    university_name: str, program_name: str, max_results: int = 6, official_domain: str | None = None
) -> list[dict]:
    """Returns list of {url, title} candidates, official sources first, aggregators excluded.

    Runs three queries: general program/requirements pages, admission-statistics pages, and a
    dedicated Common Data Set / class-profile query — without genuine selectivity data, the
    analysis model has no basis to distinguish a Reach from a Likely program. If official_domain
    is known (from program resolution), results are restricted to it.
    """
    domain_hint = f" site:{official_domain}" if official_domain else ""
    queries = [
        f"{university_name} {program_name} graduate admissions requirements official program page{domain_hint}",
        f"{university_name} {program_name} admission statistics acceptance rate average GPA GRE "
        f"admitted students class profile{domain_hint}",
        # Common Data Set / official class-profile reports are the actual primary source for real
        # admitted/enrolled-cohort statistics (not just eligibility minimums) — worth its own query.
        f"{university_name} common data set graduate {program_name} class profile enrolled students "
        f"average GPA test scores{domain_hint}",
    ]

    all_results = []
    seen_urls = set()
    for query in queries:
        for r in _tavily_search_raw(query, max_results):
            if r["url"] not in seen_urls and not _is_aggregator(r["url"]):
                seen_urls.add(r["url"])
                all_results.append(r)

    all_results.sort(key=lambda c: 0 if _looks_official(c["url"], university_name) else 1)
    return all_results[: max_results * 2]


def _looks_like_block_wall(text: str) -> bool:
    if len(text) >= BLOCK_WALL_MAX_LEN:
        return False
    text_l = text.lower()
    return any(phrase in text_l for phrase in BLOCK_WALL_PHRASES)


def fetch_page_text(url: str, timeout: int = 15) -> str | None:
    # Partial safeguard only -- see robots_check.py docstring. Applies to every fetch, official
    # and community-outcome pages alike, since both go through this shared function.
    if not robots_check.is_fetch_allowed(url):
        return None
    try:
        resp = httpx.get(url, timeout=timeout, follow_redirects=True,
                          headers={"User-Agent": "GradPilotBot/0.1"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())

        if len(text) <= 200:
            return None
        if _looks_like_block_wall(text):
            return None
        return text
    except Exception:
        return None
