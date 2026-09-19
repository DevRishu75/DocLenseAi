from app.services.embedding_service import EmbeddingService
from app.storage.vectorstore import VectorStore
from app.models.user_model import User
from app.models.document_model import Document
from sqlalchemy.orm import Session
from app.exception_handling.document_exception import DocumentNotFoundError
class RetrievalService:
    ''' WE will take the text from user and use embeddings ''' 
    def __init__(self):
        self.embed_service = EmbeddingService()
        self.vector_search = VectorStore()

    def retrieve(self,question:str,document_id,db:Session,current_user:User):
        document = db.query(Document).filter(Document.user_id==current_user.user_id,Document.id==document_id).first()
        if document is None:
            raise DocumentNotFoundError(
                message="User don't have this document",
                status_code=404,
                error_code="DOCUMENT_NOT_FOUND_ERROR"
            )
        embeddings = self.embed_service.embed_text(question)
        retreived_chunks = self.vector_search.search(embeddings,str(document.id))
        return retreived_chunks