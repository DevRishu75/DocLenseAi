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
        ids = vector_result.get("ids",[[]])[0]
        metadatas = vector_result.get("metadata",[[]])[0]
        distances = vector_result.get("distance",[[]])[0]
        # Reorder every result using the same original index
        sorted_ids = []
        sorted_chunks = []
        sorted_metadatas = []
        sorted_distances = []
        for item in keyword_result:
            index = item["index"]
            sorted_chunks.append(chunks[index])
            sorted_ids.append(ids[index])
            sorted_metadatas.append(metadatas[index])
            sorted_distances.append(distances[index])
        vector_result["documents"] = [
            sorted_chunks
        ]
        vector_result["ids"]=[
            sorted_ids
        ]
        vector_result["metadatas"]=[
            sorted_metadatas
        ]
        vector_result["distances"]=[
            sorted_distances
        ]

        return vector_result