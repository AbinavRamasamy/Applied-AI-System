from google.genai import types

from src.clients import google_client, GEMMA_MODEL

def generate_final_answer(query: str, context: str, source: str) -> str:
    prompt = f"""You are a helpful assistant. Answer the user's question using only the provided context.
If the context does not fully answer the question, say so honestly.

Source: {source}

Context:
{context}

Question: {query}

Answer:"""

    response = google_client.models.generate_content(
        model=GEMMA_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3),
    )
    return response.text.strip()
