from app.services.retrieval_service import RetrievalService
from app.services.keyword_service import KeywordSearch
class HybridSearch:

    def __init__(self):
        self.retrieval_chunk = RetrievalService()
        self.keyword_search = KeywordSearch()

    def search(self,question,document_id,db,current_user):
        vector_result = self.retrieval_chunk.retrieve(question=question,document_id=document_id,db=db,current_user=current_user)
        print("\n===== VECTOR RESULT DEBUG =====")
        print("documents:", len(vector_result.get("documents", [[]])[0]))
        print("ids:", len(vector_result.get("ids", [[]])[0]))
        print("metadatas:", len(vector_result.get("metadatas", [[]])[0]))
        print("distances:", len(vector_result.get("distances", [[]])[0]))

        print("documents:", vector_result.get("documents"))
        print("ids:", vector_result.get("ids"))
        print("metadatas:", vector_result.get("metadatas"))
        print("distances:", vector_result.get("distances"))
        print("================================\n")
        chunks = vector_result.get('documents',[[]])[0]
        ids = vector_result.get("ids", [[]])[0]
        metadatas = vector_result.get("metadatas", [[]])[0]
        distances = vector_result.get("distances", [[]])[0]

        print("\n===== VECTOR RESULT DEBUG =====")
        print("chunks:", len(chunks))
        print("ids:", len(ids))
        print("metadatas:", len(metadatas))
        print("distances:", len(distances))
        print("================================\n")
        keyword_result = self.keyword_search.search(question=question,chunks=chunks)
        sorted_chunks = [
            item["chunk"]
            for item in keyword_result
        ]
        # ids = vector_result.get("ids",[[]])[0]
        # metadatas = vector_result.get("metadata",[[]])[0]
        # distances = vector_result.get("distance",[[]])[0]
        # # Reorder every result using the same original index
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