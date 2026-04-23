from src.clients import travily_client

def get_web_results(query: str, max_results: int = 3) -> str:
    response = travily_client.search(query=query, max_results=max_results)
    snippets = [
        f"[{r.get('url', '')}]\n{r.get('content', '')}"
        for r in response.get("results", [])
    ]

    return "\n\n".join(snippets)
