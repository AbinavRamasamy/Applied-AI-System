from google.genai import types

from src.clients import google_client, GEMMA_MODEL

def get_document_relevance(query: str, context: str) -> str:
    prompt = f"""You are a relevance evaluator. Decide if the retrieved context contains enough information to answer the query.

Query: {query}

Context:
{context}

Reply with exactly one word — "relevant", "irrelevant", or "ambiguous":
- relevant   → context directly answers the query
- irrelevant → context does not address the query at all
- ambiguous  → context is partially related but incomplete"""

    response = google_client.models.generate_content(
        model=GEMMA_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(max_output_tokens=10, temperature=0),
    )
    verdict = response.text.strip().lower().split()[0]
    return verdict if verdict in ("relevant", "irrelevant", "ambiguous") else "ambiguous"
