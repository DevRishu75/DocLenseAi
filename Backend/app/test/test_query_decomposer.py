from app.services.LLM_service import LLMService
from app.services.query_decomposer import QueryDecomposer

llm_service = LLMService()
decomposer = QueryDecomposer(llm_service)

question = decomposer.decompose("How many homes come under this HOA and what will be the cost for replacing the roof?"
)
print(question)