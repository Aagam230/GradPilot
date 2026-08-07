from unittest.mock import patch, MagicMock
import httpx
import app.services.robots_check as robots_check


def _make_response(status: int, text: str = ""):
    r = MagicMock()
    r.status_code = status
    r.text = text
    if status >= 400:
        r.raise_for_status.side_effect = httpx.HTTPStatusError("err", request=None, response=r)
    else:
        r.raise_for_status.return_value = None
    return r


def test_explicit_disallow_blocks_only_that_path():
    with patch("httpx.get", return_value=_make_response(200, "User-agent: *\nDisallow: /private/\n")):
        robots_check._cache.clear()
        assert robots_check.is_fetch_allowed("https://example.com/private/secret") is False
        assert robots_check.is_fetch_allowed("https://example.com/public/page") is True


def test_no_robots_txt_allows_everything():
    with patch("httpx.get", return_value=_make_response(404)):
        robots_check._cache.clear()
        assert robots_check.is_fetch_allowed("https://example.com/anything") is True


def test_network_error_fails_closed():
    with patch("httpx.get", side_effect=httpx.ConnectError("boom")):
        robots_check._cache.clear()
        assert robots_check.is_fetch_allowed("https://example.com/anything") is False


def test_server_error_fails_closed():
    with patch("httpx.get", return_value=_make_response(500)):
        robots_check._cache.clear()
        assert robots_check.is_fetch_allowed("https://example.com/anything") is False


def test_robots_txt_fetched_once_per_domain():
    call_count = {"n": 0}

    def counted_get(*args, **kwargs):
        call_count["n"] += 1
        return _make_response(200, "User-agent: *\nAllow: /\n")

    with patch("httpx.get", side_effect=counted_get):
        robots_check._cache.clear()
        robots_check.is_fetch_allowed("https://example.com/a")
        robots_check.is_fetch_allowed("https://example.com/b")
        assert call_count["n"] == 1
