from app.services.web_search import _is_aggregator, _looks_like_block_wall, _looks_official


def test_aggregator_domains_blocked():
    assert _is_aggregator("https://www.niche.com/colleges/harvard-university/") is True
    assert _is_aggregator("https://www.gradschools.com/programs/computer-science") is True
    assert _is_aggregator("https://www.reddit.com/r/gradadmissions") is True
    assert _is_aggregator("https://cs.stanford.edu/admissions") is False


def test_block_wall_detection_on_short_pages_only():
    assert _looks_like_block_wall(
        "Please enable JavaScript and cookies to continue. Checking your browser before accessing."
    ) is True
    # A long real page that happens to mention cookies once in a footer should NOT be flagged.
    long_page = "The MS in Computer Science requires a bachelor's degree and GRE scores. " * 30
    long_page += " we use cookies to improve your experience"
    assert _looks_like_block_wall(long_page) is False


def test_official_domain_heuristic():
    assert _looks_official("https://cs.stanford.edu/admissions", "Stanford University") is True
    assert _looks_official("https://www.niche.com/x", "Stanford University") is False
    assert _looks_official("https://www.arizonastate.edu/admissions", "Arizona State University") is True
