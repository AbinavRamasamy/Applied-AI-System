from unittest.mock import patch

import src.main as main_module
from src.main import run_crag_pipeline


# Patch all external calls so every test is self-contained.
PATCHES = {
    "ensure_index": "src.main._ensure_index",
    "retrieve":     "src.main.retrieve_context",
    "evaluate":     "src.main.get_document_relevance",
    "web":          "src.main.get_web_results",
    "generate":     "src.main.generate_final_answer",
}


def test_empty_query_returns_prompt():
    assert run_crag_pipeline("") == "Please enter a question."
    assert run_crag_pipeline("   ") == "Please enter a question."


def test_relevant_path_uses_local_docs():
    with patch(PATCHES["ensure_index"]), \
         patch(PATCHES["retrieve"], return_value="local context"), \
         patch(PATCHES["evaluate"], return_value="relevant"), \
         patch(PATCHES["generate"], return_value="answer") as mock_gen, \
         patch(PATCHES["web"]) as mock_web:

        result = run_crag_pipeline("What is X?")

        mock_gen.assert_called_once_with("What is X?", "local context", source="local documents")
        mock_web.assert_not_called()
        assert result == "answer"


def test_irrelevant_path_uses_web():
    with patch(PATCHES["ensure_index"]), \
         patch(PATCHES["retrieve"], return_value="local context"), \
         patch(PATCHES["evaluate"], return_value="irrelevant"), \
         patch(PATCHES["web"], return_value="web context") as mock_web, \
         patch(PATCHES["generate"], return_value="answer") as mock_gen:

        result = run_crag_pipeline("What is Y?")

        mock_web.assert_called_once()
        mock_gen.assert_called_once_with("What is Y?", "web context", source="web search")
        assert result == "answer"


def test_ambiguous_path_blends_sources():
    with patch(PATCHES["ensure_index"]), \
         patch(PATCHES["retrieve"], return_value="local ctx"), \
         patch(PATCHES["evaluate"], return_value="ambiguous"), \
         patch(PATCHES["web"], return_value="web ctx"), \
         patch(PATCHES["generate"], return_value="blended answer") as mock_gen:

        result = run_crag_pipeline("What is Z?")

        combined = mock_gen.call_args.args[1]
        assert "local ctx" in combined
        assert "web ctx" in combined
        assert result == "blended answer"


def test_irrelevant_with_empty_web_returns_fallback_message():
    with patch(PATCHES["ensure_index"]), \
         patch(PATCHES["retrieve"], return_value="local context"), \
         patch(PATCHES["evaluate"], return_value="irrelevant"), \
         patch(PATCHES["web"], return_value=""), \
         patch(PATCHES["generate"]) as mock_gen:

        result = run_crag_pipeline("What is Z?")

        mock_gen.assert_not_called()
        assert "could not find" in result.lower()


def test_pipeline_error_returns_safe_message():
    with patch(PATCHES["ensure_index"], side_effect=Exception("boom")):
        result = run_crag_pipeline("trigger error")
        assert "error" in result.lower()
