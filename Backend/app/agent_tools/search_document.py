from sqlalchemy.orm import Session

from app.models.user_model import User
from app.services.hybrid_search_service import HybridSearch

def search_document(
        question:str,
        document_id:str,
        db:Session,
        current_user:User
):
    hybrid_Search = HybridSearch()
    return hybrid_Search.search(
        question=question,
        document_id=document_id,
        db=db,
        current_user=current_user
    )