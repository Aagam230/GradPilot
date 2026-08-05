"""Web search + fetch for official university program information.

Prioritizes official university domains (.edu, ac.uk, university name match).
Uses Tavily search API (TAVILY_API_KEY). If no key is configured or no
results are found, returns an empty list rather than fabricating content.
"""
import re
import httpx
from bs4 import BeautifulSoup
from ..config import settings

OFFICIAL_HINTS = [".edu", "ac.uk", "ac.jp", "ac.nz", "edu.au", "uni-", ".ac.", "university"]


def _looks_official(url: str, university_name: str) -> bool:
    url_l = url.lower()
    if any(h in url_l for h in OFFICIAL_HINTS):
        return True
    tokens = [t.lower() for t in re.findall(r"[A-Za-z]+", university_name) if len(t) > 3]
    return any(t in url_l for t in tokens)


def search_program_pages(university_name: str, program_name: str, max_results: int = 6) -> list[dict]:
    """Returns list of {url, title} candidates, official sources first.

    Runs two queries: one for general program/requirements pages, one specifically for
    selectivity signals (acceptance rate, admitted-student profile, class stats) — without
    those, the analysis model has no basis to distinguish a Reach from a Likely program.
    """
    if not settings.tavily_api_key:
        return []

    queries = [
        f"{university_name} {program_name} graduate admissions requirements official program page",
        f"{university_name} {program_name} admission statistics acceptance rate average GPA GRE "
        f"admitted students class profile",
    ]

    all_results = []
    seen_urls = set()
    for query in queries:
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
        except Exception as e:
            print(f"TAVILY SEARCH ERROR: {type(e).__name__}: {e}")
            continue
        for r in results:
            url = r.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append({"url": url, "title": r.get("title", "")})

    all_results.sort(key=lambda c: 0 if _looks_official(c["url"], university_name) else 1)
    return all_results[: max_results * 2]


def fetch_page_text(url: str, timeout: int = 15) -> str | None:
    try:
        resp = httpx.get(url, timeout=timeout, follow_redirects=True,
                          headers={"User-Agent": "GradPilotBot/0.1"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        # PostgreSQL TEXT cannot store NUL (0x00) characters found on some web pages.
        text = text.replace("\x00", "")
        return text if len(text) > 200 else None
    except Exception as e:
        print(f"PAGE FETCH ERROR [{url}]: {type(e).__name__}: {e}")
        return None
