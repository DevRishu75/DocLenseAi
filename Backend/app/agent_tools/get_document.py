from sqlalchemy.orm import Session
from app.services.document_service import DocumentService
from app.models.user_model import User

def get_document(document_id:str,db:Session,current_user:User):
    document = DocumentService()
    return document.get_document(
        document_id=document_id,
        db=db,
        current_user=current_user
    )