from sqlalchemy.orm import Session

from app.models.user_model import User
from app.services.hybrid_search_service import HybridSearch
from app.services.query_decomposer import QueryDecomposer
from app.services.LLM_service import LLMService


class SearchDocumentTool:
    """Bounded document search for agent calls.

    A decomposed question can otherwise trigger many searches and return a large,
    duplicated Chroma response to the agent. Keep both the number of searches and
    the final context returned to the agent predictable.
    """

    MAX_QUERIES = 4
    MAX_RESULTS = 8

    def __init__(self, hybrid_search=None, query_decomposer=None):
        self.hybrid_search = hybrid_search or HybridSearch()
        self.query_decomposer = query_decomposer

    def search(
        self,
        question: str,
        document_id: str,
        db: Session,
        current_user: User,
    ) -> dict:
        question = question.strip()
        if not question:
            return {"queries": [], "results": []}

        try:
            decomposer = self.query_decomposer or QueryDecomposer(LLMService())
            queries = (
                decomposer.decompose(question)
                if decomposer.should_decompose(question)
                else [question]
            )
            if not isinstance(queries, list):
                queries = [question]
            queries = list(dict.fromkeys(
                query.strip()
                for query in queries
                if isinstance(query, str) and query.strip()
            ))[: self.MAX_QUERIES]
        except Exception:
            # Query splitting is optional; the original question remains usable.
            queries = [question]

        if not queries:
            queries = [question]

        query_results = []
        for query in queries:
            response = self.hybrid_search.search(
                question=query,
                document_id=document_id,
                db=db,
                current_user=current_user,
            ) or {}

            documents = (response.get("documents") or [[]])[0] or []
            ids = (response.get("ids") or [[]])[0] or []
            metadatas = (response.get("metadatas") or [[]])[0] or []
            distances = (response.get("distances") or [[]])[0] or []
            row_count = min(len(documents), len(ids), len(metadatas), len(distances))

            query_results.append([
                (ids[index], documents[index], metadatas[index] or {}, distances[index])
                for index in range(row_count)
            ])

        # Interleave rankings so the first subquery cannot consume the whole
        # result budget before the remaining information needs are represented.
        results = []
        seen_ids = set()
        max_rank = max((len(rows) for rows in query_results), default=0)
        for rank in range(max_rank):
            for rows in query_results:
                if rank >= len(rows):
                    continue
                chunk_id, text, metadata, distance = rows[rank]
                if chunk_id in seen_ids:
                    continue
                seen_ids.add(chunk_id)
                results.append({
                    "chunk_id": chunk_id,
                    "text": text,
                    "metadata": metadata,
                    "distance": distance,
                })
                if len(results) >= self.MAX_RESULTS:
                    break
            if len(results) >= self.MAX_RESULTS:
                break

        return {"queries": queries, "results": results}


def search_document(
    question: str,
    document_id: str,
    db: Session,
    current_user: User,
) -> dict:
    return SearchDocumentTool().search(
        question=question,
        document_id=document_id,
        db=db,
        current_user=current_user,
    )
