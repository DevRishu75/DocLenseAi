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

        if self.query_decomposer.should_decompose(question):
            queries = self.query_decomposer.decompose(question=question)
        else:
            queries = [question]
        print(
            f"Query Decomposition"
            f"{time.perf_counter()-start:.2f}s"
        )
        start = time.perf_counter()
        for querie in queries:
             retrieved_chunks = self.hybrid_retrieve.search(
                         question=querie,
                         document_id=document_id,
                         db=db,
                         current_user=current_user
                     )
        
        print(
            f"retrieval time"
            f"{time.perf_counter()-start:.2f}s"
        )
        chunks_ids = retrieved_chunks.get('ids',[[]])[0]
        metadatas = retrieved_chunks.get('metadatas',[[]])[0]
        distances = retrieved_chunks.get('distances',[[]])[0]
        
        chunks = retrieved_chunks.get('documents',[[]])[0]
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

        print(
          f"Final LLM generation: "
          f"{time.perf_counter() - start:.2f}s"
        )
        return{
            "answer": answer,
            "sources": sources
        }