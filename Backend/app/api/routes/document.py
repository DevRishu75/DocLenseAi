from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.document_response import DocumentResponse
from app.services.document_service import DocumentService
from app.auth.dependecies import get_current_user
from app.models.user_model import User
from uuid import UUID

document_router = APIRouter()

@document_router.get('/api/v1/documents', response_model=list[DocumentResponse])
def get_documents(current_user:User = Depends(get_current_user),db: Session = Depends(get_db)):
    service = DocumentService()
    return service.get_documents(db,current_user)

@document_router.get('/api/v1/documents/{document_id}', response_model=DocumentResponse)
def get_document(document_id: UUID,db: Session = Depends(get_db), current_user:User=Depends(get_current_user)):
    service = DocumentService()
    document = service.get_document(document_id, db,current_user)
    return document

@document_router.delete('/api/v1/documents/{document_id}')
def delete_document(document_id: UUID, db: Session = Depends(get_db), current_user:User=Depends(get_current_user)):
    service = DocumentService()
    
    # Do NOT call get_document here. delete_document already handles existence check.
    result = service.delete_document(document_id, db,current_user)
    return result