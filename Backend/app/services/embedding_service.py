from sentence_transformers import SentenceTransformer
from app.exception_handling.embedding_exception import EmbeddingExceptionError
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
class EmbeddingService:
    _model = None
    def __init__(self):
        try:
             if EmbeddingService._model is None:
                    EmbeddingService._model = SentenceTransformer(MODEL_NAME)
             self.model = EmbeddingService._model
        except Exception as error:
             raise EmbeddingExceptionError(
                  message="Embedding Failure happen",
                  status_code=500,
                  error_code="EMBEDDING_ERROR"
             )from error
    def embed_text(self,text:str)->list[float]:
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as error:
             raise EmbeddingExceptionError(
                  message="Embedding Failure happen",
                  status_code=500,
                  error_code="EMBEDDING_ERROR"
             )from error
    def embed_chunks(self,chunks:list[str])->list[list[float]]:
        try:
            embeddings = self.model.encode(chunks)
            return embeddings.tolist()
        except Exception as error:
             raise EmbeddingExceptionError(
                  message="Embedding failure happen",
                  status_code=500,
                  error_code="EMBEDDING_ERROR"
             )from error
        