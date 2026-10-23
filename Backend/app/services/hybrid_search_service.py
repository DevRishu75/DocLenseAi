from app.services.retrieval_service import RetrievalService
from app.services.keyword_service import KeywordSearch


class HybridSearch:
    def __init__(self):
        self.retrieval_chunk = RetrievalService()
        self.keyword_search = KeywordSearch()

    def search(self, question, document_id, db, current_user):
        vector_result = self.retrieval_chunk.retrieve(
            question=question,
            document_id=document_id,
            db=db,
            current_user=current_user,
        )
        chunks = vector_result.get("documents", [[]])[0]
        ids = vector_result.get("ids", [[]])[0]
        metadatas = vector_result.get("metadatas", [[]])[0]
        distances = vector_result.get("distances", [[]])[0]
        keyword_results = self.keyword_search.search(question=question, chunks=chunks)

        ordered_indices = [item["index"] for item in keyword_results]
        vector_result["documents"] = [[chunks[index] for index in ordered_indices]]
        vector_result["ids"] = [[ids[index] for index in ordered_indices]]
        vector_result["metadatas"] = [[metadatas[index] for index in ordered_indices]]
        vector_result["distances"] = [[distances[index] for index in ordered_indices]]
        return vector_result
