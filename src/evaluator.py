import logging

from google.genai import types

from src.clients import google_client, GEMMA_MODEL

logger = logging.getLogger(__name__)


def get_document_relevance(query: str, context: str) -> str:
    prompt = f"""You are a relevance evaluator. Decide if the retrieved context contains enough information to answer the query.

Query: {query}

Context:
{context}

Reply with exactly one word — "relevant", "irrelevant", or "ambiguous":
- relevant   → context directly answers the query
- irrelevant → context does not address the query at all
- ambiguous  → context is partially related but incomplete"""

    try:
        response = google_client.models.generate_content(
            model=GEMMA_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=10, temperature=0),
        )
        verdict = response.text.strip().lower().split()[0]
        result = verdict if verdict in ("relevant", "irrelevant", "ambiguous") else "ambiguous"
        logger.info("Relevance verdict: %s", result)
        return result
    except Exception as e:
        logger.error("Relevance evaluation failed: %s — defaulting to 'ambiguous'.", e)
        return "ambiguous"
