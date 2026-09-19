from pathlib import Path
from sqlalchemy.orm import Session
from app.models.document_model import Document
from app.storage.vectorstore import VectorStore
from app.models.user_model import User
from app.exception_handling.document_exception import DocumentNotFoundError
from app.exception_handling.vector_exception import VectorError

class DocumentService:
    UPLOAD_FOLDER = Path('uploads')
    def __init__(self):
        self.vector_store = VectorStore()
        
    def get_documents(self,db:Session,current_user:User):
        documents =  db.query(Document).filter(Document.user_id== current_user.user_id).all()
        return [
            {
                "document_id": document.id,
                "filename": document.filename,
                "created_at": document.created_at
            }
            for document in documents
        ]
    def get_document(self,document_id,db:Session,current_user:User):
        document = db.query(Document).filter(Document.id==document_id, Document.user_id==current_user.user_id).first()
        if document is None:
            raise DocumentNotFoundError(
                message="Document Not Found",
                status_code=404,
                error_code="DOCUMENT_NOT_FOUND_ERROR"
            )
        return {
            "document_id": document.id,
            "filename": document.filename,
            "created_at":document.created_at
        }
    def delete_document(self,document_id,db:Session,current_user:User):
        document = db.query(Document).filter(Document.id==document_id,Document.user_id==current_user.user_id).first()
        if document is None:
            raise DocumentNotFoundError(
                message="Document does not exists",
                status_code=500,
                error_code="DOCUMENT_NOT_FOUND_ERROR"
            )
        file_path = self.UPLOAD_FOLDER/document.filename
        if file_path.exists():
            file_path.unlink()
        chunk_before_delete = self.vector_store.count_document_chunk(document_id)
        print(chunk_before_delete)
        self.vector_store.delete_document(document_id)
        chunk_after_delete =  self.vector_store.count_document_chunk(document_id)
        print(chunk_after_delete)
        if chunk_after_delete !=0:
            raise VectorError(
                message="Document vectors cannot be deleted",
                status_code=422,
                error_code="VECTOR_ERROR"
            )
        db.delete(document)
        db.commit()
        return {
            "document_id":str(document.id),
            "message": "Content deleted successfully"
        }