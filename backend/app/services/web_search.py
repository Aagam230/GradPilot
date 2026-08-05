"""Tavily search + fetch with official-domain validation."""
import re
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from ..config import settings

OFFICIAL_HINTS = [".edu", "ac.uk", "ac.jp", "ac.nz", "edu.au", ".ac.", "university"]


def _host(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower().removeprefix("www.")
    except Exception:
        return ""


def _on_domain(url: str, domain: str | None) -> bool:
    if not domain:
        return False
    host = _host(url)
    domain = domain.lower().removeprefix("www.")
    return host == domain or host.endswith("." + domain)


def _looks_official(url: str, university_name: str) -> bool:
    url_l = url.lower()
    if any(h in url_l for h in OFFICIAL_HINTS):
        return True
    tokens = [t.lower() for t in re.findall(r"[A-Za-z]+", university_name) if len(t) > 3]
    return any(t in _host(url) for t in tokens)


def search_program_pages(university_name: str, program_name: str, max_results: int = 6,
                         official_domain: str | None = None) -> list[dict]:
    if not settings.tavily_api_key:
        return []
    domain_clause = f" site:{official_domain}" if official_domain else " official"
    queries = [
        f'"{university_name}" "{program_name}" admissions requirements prerequisites GRE TOEFL{domain_clause}',
        f'"{university_name}" "{program_name}" curriculum degree requirements{domain_clause}',
        f'"{university_name}" "{program_name}" competitive selectivity applicants admitted cohort class profile{domain_clause}',
    ]
    all_results, seen = [], set()
    for query in queries:
        try:
            resp = httpx.post("https://api.tavily.com/search", json={
                "api_key": settings.tavily_api_key, "query": query,
                "max_results": max_results, "search_depth": "advanced",
            }, timeout=20)
            resp.raise_for_status()
            results = resp.json().get("results", [])
        except Exception as e:
            print(f"TAVILY SEARCH ERROR: {type(e).__name__}: {e}")
            continue
        for r in results:
            url = r.get("url")
            if not url or url in seen:
                continue
            # Once a canonical official domain is known, unrelated domains are rejected entirely.
            if official_domain and not _on_domain(url, official_domain):
                continue
            seen.add(url)
            all_results.append({"url": url, "title": r.get("title", ""), "official": True})
    if not official_domain:
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
        text = " ".join(soup.get_text(separator=" ").split()).replace("\x00", "")
        return text if len(text) > 200 else None
    except Exception as e:
        print(f"PAGE FETCH ERROR [{url}]: {type(e).__name__}: {e}")
        return None
