from chromadb import PersistentClient
from app.exception_handling.vector_exception import VectorError
from app.core.logging import logger
class VectorStore:
    def __init__(self):
      self.client = PersistentClient(path = 'database')
      self.collection = self.client.get_or_create_collection(name= "BoardIQ")
    def add_document(self,ids,documents,metadatas,embeddings):
        try:
            self.collection.add(
                        ids = ids,documents = documents,metadatas = metadatas,embeddings = embeddings
                    )
        except Exception as error:
            logger.exception("adding Document to vector failed")
            raise VectorError(
                message="Error while adding document to Vector DB",
                status_code=422,
                error_code="VECTOR_ERROR"
            )from error
    def search(self,embeddings,document_id,top_k :int = 5):
      try:
            return self.collection.query(query_embeddings=[embeddings],
                                               n_results = top_k, where={
                                                   'document_id':str(document_id)
                                               })
      except Exception as error:
          raise VectorError(
              message="Error while finding the same vectors inside DB",
              status_code=500,
              error_code="VECTOR_ERROR"
          )from error
    def delete_document(self,document_id):
        try:
            self.collection.delete(
                        where={
                            'document_id': str(document_id)
                        }
                    )
        except Exception as error:
            raise VectorError(
                          message="Error while finding deleting document vector inside DB",
                          status_code=400,
                          error_code="VECTOR_ERROR"
            )
    def count_document_chunk(self,document_id):
        try:
            results = self.collection.get(
                        where={
                            'document_id': str(document_id)
                        }
                    )
                # include = []
            return len(results["ids"])
        except Exception as error:
            raise VectorError(
                message="Error while counting document chunks"
            )from error