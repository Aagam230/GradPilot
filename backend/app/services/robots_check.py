"""Lightweight robots.txt check applied before fetching any external page.

This is a PARTIAL safeguard, not a substitute for reviewing a site's actual terms of service —
robots.txt only covers automated-crawling permissions, not usage/licensing terms. It does reduce
one concrete risk though: fetching a path a site has explicitly asked bots not to touch.

Fails closed: if robots.txt can't be reached/parsed at all, the fetch is blocked rather than
assumed permitted. This can reduce fetch success rate on flaky networks — that's an intentional
trade-off in favor of not guessing when we can't verify.
"""
import httpx
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

USER_AGENT = "GradPilotBot/0.1"
_ALLOW_ALL = "allow_all"
_DENY_ALL = "deny_all"

# Per-domain cache so we don't re-fetch robots.txt on every single page. Process-lifetime only —
# fine for a background retrieval job, not intended as a long-lived cache across deployments.
_cache: dict[str, object] = {}


def _get_entry(domain: str):
    if domain in _cache:
        return _cache[domain]

    robots_url = f"https://{domain}/robots.txt"
    try:
        resp = httpx.get(robots_url, timeout=8, headers={"User-Agent": USER_AGENT}, follow_redirects=True)
        if resp.status_code == 404:
            entry = _ALLOW_ALL  # no robots.txt published -> allowed by convention
        else:
            resp.raise_for_status()
            parser = RobotFileParser()
            parser.parse(resp.text.splitlines())
            entry = parser
    except Exception:
        entry = _DENY_ALL  # could not verify at all -- fail closed rather than assume permission

    _cache[domain] = entry
    return entry


def is_fetch_allowed(url: str) -> bool:
    domain = urlparse(url).netloc
    if not domain:
        return True

    entry = _get_entry(domain)
    if entry == _ALLOW_ALL:
        return True
    if entry == _DENY_ALL:
        return False
    return entry.can_fetch(USER_AGENT, url)
