from sqlalchemy.orm import Session
from app.models.user_model import User
from app.services.retrieval_service import RetrievalService

def retrieve_chunks(question:str,document_id:str,db:Session,current_user:User):
    retrieval_service = RetrievalService()
    return retrieval_service.retrieve(
        question=question,
        document_id=document_id,
        db=db,
        current_user=current_user
    )
