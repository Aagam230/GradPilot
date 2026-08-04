"""Web search + fetch for official university program information.

Prioritizes official university domains (.edu, ac.uk, university name match).
Uses Tavily search API (TAVILY_API_KEY). If no key is configured or no
results are found, returns an empty list rather than fabricating content.
"""

import re
import httpx
from bs4 import BeautifulSoup
from ..config import settings


OFFICIAL_HINTS = [
    ".edu",
    "ac.uk",
    "ac.jp",
    "ac.nz",
    "edu.au",
    "uni-",
    ".ac.",
    "university",
]


def _looks_official(url: str, university_name: str) -> bool:
    """Check whether a URL appears to belong to an official university source."""

    url_l = url.lower()

    if any(h in url_l for h in OFFICIAL_HINTS):
        return True

    tokens = [
        t.lower()
        for t in re.findall(r"[A-Za-z]+", university_name)
        if len(t) > 3
    ]

    return any(t in url_l for t in tokens)


def search_program_pages(
    university_name: str,
    program_name: str,
    max_results: int = 6,
) -> list[dict]:
    """Search Tavily for university/program pages.

    Returns a list of:
        {
            "url": "...",
            "title": "..."
        }

    Official-looking university sources are placed first.
    """

    if not settings.tavily_api_key:
        print("TAVILY SEARCH ERROR: TAVILY_API_KEY is not configured.")
        return []

    query = (
        f"{university_name} {program_name} "
        f"graduate admissions requirements official program page"
    )

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
        print(
            f"TAVILY SEARCH ERROR: "
            f"{type(e).__name__}: {e}"
        )
        return []

    candidates = []

    for result in results:
        url = result.get("url")

        if not url:
            continue

        candidates.append(
            {
                "url": url,
                "title": result.get("title", ""),
            }
        )

    # Put likely official university pages first.
    candidates.sort(
        key=lambda candidate: (
            0
            if _looks_official(
                candidate["url"],
                university_name,
            )
            else 1
        )
    )

    return candidates


def fetch_page_text(
    url: str,
    timeout: int = 15,
) -> str | None:
    """Download and clean text from a university webpage."""

    try:
        resp = httpx.get(
            url,
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "GradPilotBot/0.1",
            },
        )

        resp.raise_for_status()

        soup = BeautifulSoup(
            resp.text,
            "html.parser",
        )

        # Remove page elements that generally contain
        # navigation/boilerplate rather than program information.
        for tag in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
            ]
        ):
            tag.decompose()

        text = " ".join(
            soup.get_text(separator=" ").split()
        )

        # PostgreSQL TEXT fields cannot contain NUL (0x00).
        # Some webpages may contain these characters.
        text = text.replace("\x00", "")

        # Ignore pages that contain almost no useful text.
        if len(text) <= 200:
            return None

        return text

    except Exception as e:
        print(
            f"PAGE FETCH ERROR [{url}]: "
            f"{type(e).__name__}: {e}"
        )
        return None