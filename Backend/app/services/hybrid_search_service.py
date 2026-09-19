from app.services.retrieval_service import RetrievalService
from app.services.keyword_service import KeywordSearch
class HybridSearch:

    def __init__(self):
        self.retrieval_chunk = RetrievalService()
        self.keyword_search = KeywordSearch()

    def search(self,question,document_id,db,current_user):
        vector_result = self.retrieval_chunk.retrieve(question=question,document_id=document_id,db=db,current_user=current_user)
        chunks = vector_result.get('documents',[[]])[0]
        keyword_result = self.keyword_search.search(question=question,chunks=chunks)
        sorted_chunks = [
            item["chunk"]
            for item in keyword_result
        ]
        vector_result["documents"] = [
            sorted_chunks
        ]
        return vector_result