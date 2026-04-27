from unittest.mock import MagicMock, patch

from src.web_tools import get_web_results


def _fake_search_response(results: list) -> dict:
    return {"results": results}


@patch("src.web_tools.tavily_client")
def test_formats_results(mock_client):
    mock_client.search.return_value = _fake_search_response([
        {"url": "https://example.com", "content": "some content"},
        {"url": "https://other.com", "content": "more content"},
    ])
    result = get_web_results("test query")
    assert "https://example.com" in result
    assert "some content" in result
    assert "https://other.com" in result


@patch("src.web_tools.tavily_client")
def test_empty_results_returns_empty_string(mock_client):
    mock_client.search.return_value = _fake_search_response([])
    assert get_web_results("query") == ""


@patch("src.web_tools.tavily_client")
def test_api_failure_returns_empty_string(mock_client):
    mock_client.search.side_effect = Exception("rate limited")
    assert get_web_results("query") == ""
