from app.services.LLM_service import LLMService

llm = LLMService()

response = llm.generate(
    "Explain what is in a database in two sentence"
)
print(response)