from unittest.mock import MagicMock, patch

from src.generator import generate_final_answer


def _mock_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.text = text
    return resp


@patch("src.generator.google_client")
def test_returns_generated_answer(mock_client):
    mock_client.models.generate_content.return_value = _mock_response("  The answer is 42.  ")
    result = generate_final_answer("What is the answer?", "context here", "local documents")
    assert result == "The answer is 42."


@patch("src.generator.google_client")
def test_source_label_passed_through(mock_client):
    mock_client.models.generate_content.return_value = _mock_response("answer")
    generate_final_answer("q", "ctx", "web search")
    call_args = mock_client.models.generate_content.call_args
    # The source label should appear in the prompt sent to the model.
    prompt = call_args.kwargs.get("contents") or call_args.args[1]
    assert "web search" in prompt


@patch("src.generator.google_client")
def test_api_failure_returns_error_message(mock_client):
    mock_client.models.generate_content.side_effect = Exception("network error")
    result = generate_final_answer("q", "ctx", "local documents")
    assert "error" in result.lower()
