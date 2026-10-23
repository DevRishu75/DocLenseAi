from app.services.LLM_service import LLMService
from app.services.hybrid_search_service import HybridSearch
from app.services.releavance_service import RelevanceService
from app.services.query_decomposer import QueryDecomposer
from app.prompts.rag_prompts import build_rag_prompt
from app.core.logging import logger
import time

class QueryService:
    MAX_COUNT_CHUNKS = 10
    def __init__(self):
        self.llm_service = LLMService()
        self.hybrid_retrieve = HybridSearch()
        self.relevance_service = RelevanceService()
        self.query_decomposer = QueryDecomposer(self.llm_service)
    def ask(self,question,document_id,db,current_user):
        start = time.perf_counter()

        try:
            if self.query_decomposer.should_decompose(question):
                queries = self.query_decomposer.decompose(question=question)
            else:
                queries = [question]
            if not isinstance(queries, list):
                queries = [question]
            queries = list(dict.fromkeys(
                query.strip()
                for query in queries
                if isinstance(query, str) and query.strip()
            ))[:4]
            if not queries:
                queries = [question]
        except Exception:
            logger.exception("Question decomposition failed; retrieving with the original question")
            queries = [question]
        print(
            f"Query Decomposition"
            f"{time.perf_counter()-start:.2f}s"
        )
        start = time.perf_counter()
        retrieved_results = []
        for querie in queries:
             retrieved_results.append(self.hybrid_retrieve.search(
                         question=querie,
                         document_id=document_id,
                         db=db,
                         current_user=current_user
                     ))
        if len(retrieved_results) == 1:
             retrieved_chunks = retrieved_results[0]
             chunks = retrieved_chunks.get('documents',[[]])[0]
             chunks_ids = retrieved_chunks.get('ids',[[]])[0]
             metadatas = retrieved_chunks.get('metadatas',[[]])[0]
             distances = retrieved_chunks.get('distances',[[]])[0]
        else:
             chunks, chunks_ids, metadatas, distances = [], [], [], []
             seen_chunk_ids = set()
             unpacked = [
                 (result.get('documents',[[]])[0], result.get('ids',[[]])[0],
                  result.get('metadatas',[[]])[0], result.get('distances',[[]])[0])
                 for result in retrieved_results
             ]
             max_rank = max((len(item[0]) for item in unpacked), default=0)
             for rank in range(max_rank):
                 for query_chunks, query_ids, query_metadata, query_distances in unpacked:
                     if rank >= min(len(query_chunks), len(query_ids), len(query_metadata), len(query_distances)):
                         continue
                     chunk_id = query_ids[rank]
                     if chunk_id in seen_chunk_ids:
                         continue
                     seen_chunk_ids.add(chunk_id)
                     chunks.append(query_chunks[rank])
                     chunks_ids.append(chunk_id)
                     metadatas.append(query_metadata[rank])
                     distances.append(query_distances[rank])
        print(
            f"retrieval time"
            f"{time.perf_counter()-start:.2f}s"
        )
        if not chunks:
                return{
                    "answer":("I could not find the relevant information about the query."),
                    "sources":[]
                }
        #step 4: Filter relevant chunks
        relevant_chunks = []
        sources = []
        for chunk, chunk_id,metadata,distance in zip(
            chunks, chunks_ids,metadatas,distances
        ):
            # print(f"\nDistance: {distance}")

            # print(f"\nChunk:\n{chunk}")
            logger.debug(
                 "Retrieved chunks",
                 extra={
                      "chunk_id":chunk_id,
                      "distance":distance
                 }
            )
        
            relevance_score = self.relevance_service.calculate_score(distance)

            if self.relevance_service.is_relevant(relevance_score):
                relevant_chunks.append(chunk)
                sources.append(
                               {
                                    "chunk_id": chunk_id,
                                    "chunk_index":metadata.get("chunk_index"),
                                    "page_number": metadata.get("page_number"),
                                    "source": metadata.get("source"),
                                    "relevance_score":relevance_score
                               }
                            )
            if len(relevant_chunks)>=self.MAX_COUNT_CHUNKS:
                 break
            # If not relevant chunks found then -- 
        if not relevant_chunks:
             return {
                            "answer": (
                                "I could not find relevant information "
                                "about your question in this document."
                            ),
                            "sources": []
                        }
         
        context = "\n\n".join(relevant_chunks)
        prompt = build_rag_prompt(context,question)
        print("\n========== FINAL RAG CONTEXT ==========")
        print(context)
        print("=======================================\n")
        start = time.perf_counter()

        answer = self.llm_service.generate(prompt)
        if answer.strip().lower().startswith("user safety:"):
            logger.warning("LLM returned a safety label instead of an answer; retrying once")
            answer = self.llm_service.generate(
                prompt + "\n\nAnswer the document question directly using the provided document. "
                "Do not return a safety classification or safety label."
            )
            if answer.strip().lower().startswith("user safety:"):
                answer = "I could not produce a document answer just now. Please retry the question."

        print(
          f"Final LLM generation: "
          f"{time.perf_counter() - start:.2f}s"
        )
        return{
            "answer": answer,
            "sources": sources
        }
