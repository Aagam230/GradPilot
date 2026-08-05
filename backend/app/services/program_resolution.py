"""Canonical program/institution resolution without changing the existing stack."""
import re
from urllib.parse import urlparse

KNOWN = [
    {
        "university_aliases": ["nus", "national university of singapore"],
        "canonical_university": "National University of Singapore",
        "official_domain": "nus.edu.sg",
        "program_aliases": {
            "Master of Computing (Computer Science Specialisation)": [
                "mcomp cs", "mcomp computer science", "master of computing computer science",
                "master of computing cs", "master of computing (computer science specialisation)",
                "master of computing computer science specialisation",
            ],
            "Master of Computing in Artificial Intelligence": [
                "mcomp ai", "master of computing ai", "master of computing in artificial intelligence",
                "master of computing artificial intelligence",
            ],
            "Master of Computing (General Track)": [
                "mcomp general", "mcomp general track", "master of computing general track",
            ],
        },
    },
    {
        "university_aliases": ["asu", "arizona state", "arizona state university"],
        "canonical_university": "Arizona State University",
        "official_domain": "asu.edu",
        "program_aliases": {
            "MS in Computer Science": [
                "ms computer science", "ms in computer science", "computer science ms",
                "master of science computer science", "master of science in computer science",
            ],
        },
    },
]


def _norm(value: str) -> str:
    value = (value or "").lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def domain_from_url(url: str | None) -> str | None:
    if not url or url == "user-provided":
        return None
    try:
        host = (urlparse(url).hostname or "").lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return None


def resolve_program(university_name: str, program_name: str, seed_url: str | None = None) -> dict:
    """Resolve common aliases deterministically; otherwise preserve normalized user input.

    This intentionally does not invent a program. Unknown names remain user-provided until official
    retrieval provides stronger evidence.
    """
    u = _norm(university_name)
    p = _norm(program_name)
    for item in KNOWN:
        if u in {_norm(x) for x in item["university_aliases"]}:
            canonical_program = program_name.strip()
            for name, aliases in item["program_aliases"].items():
                if p == _norm(name) or p in {_norm(x) for x in aliases}:
                    canonical_program = name
                    break
            return {
                "canonical_university_name": item["canonical_university"],
                "canonical_program_name": canonical_program,
                "official_domain": item["official_domain"],
                "program_url": seed_url,
            }

    return {
        "canonical_university_name": " ".join((university_name or "").split()),
        "canonical_program_name": " ".join((program_name or "").split()),
        "official_domain": domain_from_url(seed_url),
        "program_url": seed_url,
    }
