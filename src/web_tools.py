import logging

from src.clients import tavily_client

logger = logging.getLogger(__name__)


def get_web_results(query: str, max_results: int = 3) -> str:
    try:
        logger.info("Running web search for query: %s", query)
        response = tavily_client.search(query=query, max_results=max_results)
        snippets = [
            f"[{r.get('url', '')}]\n{r.get('content', '')}"
            for r in response.get("results", [])
        ]
        logger.info("Web search returned %d results.", len(snippets))
        return "\n\n".join(snippets)
    except Exception as e:
        logger.error("Web search failed: %s", e)
        return ""
