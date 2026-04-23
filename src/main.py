from src.retriever import retrieve_context, load_and_index_pdfs, data_folder
from src.evaluator import get_document_relevance
from src.web_tools import get_web_results
from src.generator import generate_final_answer

_pdfs_loaded = False


def _ensure_index():
    global _pdfs_loaded
    if not _pdfs_loaded:
        load_and_index_pdfs(str(data_folder))
        _pdfs_loaded = True


def run_crag_pipeline(user_query: str) -> str:
    _ensure_index()

    context = retrieve_context(user_query, top_k=3)
    relevance = get_document_relevance(user_query, context) if context else "irrelevant"

    if relevance == "relevant":
        return generate_final_answer(user_query, context, source="local documents")

    elif relevance == "irrelevant":
        web_context = get_web_results(user_query)
        return generate_final_answer(user_query, web_context, source="web search")

    else:  # ambiguous — blend both sources
        web_context = get_web_results(user_query)
        combined = f"Local Documents:\n{context}\n\nWeb Search:\n{web_context}"
        return generate_final_answer(user_query, combined, source="local documents + web search")


if __name__ == "__main__":
    query = input('Ask a question from the provided documents: ')
    print(run_crag_pipeline(query))
