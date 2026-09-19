from app.services.LLM_service import LLMService
from app.services.hybrid_search_service import HybridSearch
from app.services.releavance_service import RelevanceService
from app.prompts.rag_prompts import build_rag_prompt
from app.core.logging import logger


class QueryService:
    MAX_COUNT_CHUNKS = 5
    def __init__(self):
        self.llm_service = LLMService()
        self.hybrid_retrieve = HybridSearch()
        self.relevance_service = RelevanceService()
    def ask(self,question,document_id,db,current_user):
        retrieved_chunks = self.hybrid_retrieve.search(
            question=question,
            document_id=document_id,
            db=db,
            current_user=current_user
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

            relevant_chunks.append(chunk)
            sources.append(
               {
                    "chunk_id": chunk_id,
                    "chunk_index":metadata.get("chunk_index"),
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
        answer = self.llm_service.generate(prompt)
        
        return{
            "answer": answer,
            "sources": sources
        }