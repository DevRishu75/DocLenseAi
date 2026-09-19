from ollama import chat
from app.exception_handling.llm_exception import LLMExceptionError
class LLMService:
    def generate(self,prompt:str)->str:
        try:
            response = chat(
                        model="gemma2:2b",
                        messages=[
                            {
                                "role":"user",
                                "content":prompt
                            }
                        ]
                    )
            return response["message"]["content"]
        except Exception as error:
            raise LLMExceptionError(
                message="LLM Error",
                status_code=500,
                error_code="LLM_ERROR"
            )from error


        
