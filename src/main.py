import logging

from src.retriever import retrieve_context, load_and_index_pdfs, data_folder
from src.evaluator import get_document_relevance
from src.web_tools import get_web_results
from src.generator import generate_final_answer

logger = logging.getLogger(__name__)

_pdfs_loaded = False


def _ensure_index():
    global _pdfs_loaded
    if not _pdfs_loaded:
        logger.info("Loading and indexing PDFs from '%s'.", data_folder)
        load_and_index_pdfs(str(data_folder))
        _pdfs_loaded = True


def run_crag_pipeline(user_query: str) -> str:
    if not user_query or not user_query.strip():
        return "Please enter a question."

    try:
        _ensure_index()

        context = retrieve_context(user_query, top_k=3)
        relevance = get_document_relevance(user_query, context) if context else "irrelevant"
        logger.info("Pipeline routing: relevance=%s", relevance)

        if relevance == "relevant":
            return generate_final_answer(user_query, context, source="local documents")

        elif relevance == "irrelevant":
            web_context = get_web_results(user_query)
            if not web_context:
                return "I could not find relevant information in local documents or via web search."
            return generate_final_answer(user_query, web_context, source="web search")

        else:  # ambiguous — blend both sources
            web_context = get_web_results(user_query)
            combined = f"Local Documents:\n{context}\n\nWeb Search:\n{web_context}"
            return generate_final_answer(user_query, combined, source="local documents + web search")

    except Exception as e:
        logger.error("Pipeline error for query '%s': %s", user_query, e)
        return "An unexpected error occurred. Please check the logs and try again."


if __name__ == "__main__":
    query = input("Ask a question from the provided documents: ")
    print(run_crag_pipeline(query))
