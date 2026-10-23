import os

from dotenv import load_dotenv
from openrouter import OpenRouter

from app.core.logging import logger

from app.exception_handling.llm_exception import LLMExceptionError

load_dotenv()


class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured")

        self.client = OpenRouter(api_key=api_key)

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.send(
                model="openrouter/free",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            if not response.choices:
                raise ValueError("The LLM returned no choices")

            content = response.choices[0].message.content

            if not isinstance(content, str) or not content.strip():
                raise ValueError("The LLM returned empty content")

            return content

        except Exception as error:
            logger.exception("LLM request failed")
            raise LLMExceptionError(
                message="LLM Error",
                status_code=500,
                error_code="LLM_ERROR",
            ) from error