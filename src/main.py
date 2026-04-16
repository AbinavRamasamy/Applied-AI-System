from src.retriever import retrieve_context
from src.evaluator import get_document_relevance
from src.web_tools import get_web_results
from src.generator import generate_final_answer

def run_crag_pipeline(user_query: str) -> str:
    return ''

if __name__ == "__main__":
    query = input('Ask a question from the provided documents:')
    run_crag_pipeline(query)
