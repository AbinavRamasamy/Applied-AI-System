from unittest.mock import MagicMock, patch

from src.evaluator import get_document_relevance


def _mock_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.text = text
    return resp


@patch("src.evaluator.google_client")
def test_returns_relevant(mock_client):
    mock_client.models.generate_content.return_value = _mock_response("relevant")
    assert get_document_relevance("q", "some context") == "relevant"


@patch("src.evaluator.google_client")
def test_returns_irrelevant(mock_client):
    mock_client.models.generate_content.return_value = _mock_response("irrelevant")
    assert get_document_relevance("q", "some context") == "irrelevant"


@patch("src.evaluator.google_client")
def test_returns_ambiguous(mock_client):
    mock_client.models.generate_content.return_value = _mock_response("ambiguous")
    assert get_document_relevance("q", "some context") == "ambiguous"


@patch("src.evaluator.google_client")
def test_unexpected_verdict_defaults_to_ambiguous(mock_client):
    # Model returns something outside the three valid words.
    mock_client.models.generate_content.return_value = _mock_response("maybe")
    assert get_document_relevance("q", "some context") == "ambiguous"


@patch("src.evaluator.google_client")
def test_api_failure_defaults_to_ambiguous(mock_client):
    mock_client.models.generate_content.side_effect = Exception("timeout")
    assert get_document_relevance("q", "some context") == "ambiguous"
