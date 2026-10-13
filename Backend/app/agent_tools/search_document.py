from sqlalchemy.orm import Session

from app.models.user_model import User
from app.services.hybrid_search_service import HybridSearch
from app.services.query_decomposer import QueryDecomposer
from app.services.LLM_service import LLMService


def search_document(
        question:str,
        document_id:str,
        db:Session,
        current_user:User
):
    hybrid_Search = HybridSearch()
    quries = QueryDecomposer(LLMService)
    if quries.should_decompose(question):
        queries = quries.decompose(question)
    else:
        queries = [question]

    results = []
    for query in queries:
        result =  hybrid_Search.search(
        question=query,
        document_id=document_id,
        db=db,
        current_user=current_user
    )
    results.append(result)
    return results