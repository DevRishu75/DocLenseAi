from app.services.LLM_service import LLMService
import json

class QueryDecomposer:
    MAX_QUERY_DECOMPOSER_WORDS = 10
    Reference_words ={
         "it",
        "this",
        "that",
        "these",
        "those",
        "they",
        "them",
        "above",
        "below",
        "respectively",
    }
    def __init__(self,llm_service:LLMService):
        self.llm_service = llm_service
    def should_decompose(self,question:str):
        words = question.split()
        if len(words)<=self.MAX_QUERY_DECOMPOSER_WORDS:
            return False
        question_words = {
            word.strip(".,!?;:()[]{}").lower()
            for word in words
        }
        if question_words.intersection(self.Reference_words):
            return False
        return True
    def decompose(self,question:str)->list[str]:
        prompt = f"""
You are a query decomposition system for a document retrieval system.

Your job is to determine whether the user's question contains
multiple independent information needs.

If the question contains only ONE information need,
return the original question unchanged as a JSON array containing
exactly one string.

If the question contains TWO OR MORE independent information needs,
split it into separate search questions.

IMPORTANT RULES:

1. Do not split a question merely because it is long.
2. Split only when there are multiple independent information needs.
3. If one part of the question depends on another part,
   keep them together.
4. Preserve references such as:
   "it", "this", "that", "these", "those", "the above",
   "respectively", etc.
5. Do not remove information required to understand the question.
6. Do not answer the question.
7. Do not add information that is not present in the user's question.
8. Return ONLY a JSON array of strings.

Examples:

Input:
"How many homes are in the HOA?"

Output:
[
    "How many homes are in the HOA?"
]

Input:
"How many homes are in the HOA and when will the roof be replaced?"

Output:
[
    "How many homes are in the HOA?",
    "When will the roof be replaced?"
]

Input:
"How much will the roof replacement cost and when is it scheduled?"

Output:
[
    "How much will the roof replacement cost?",
    "When is the roof replacement scheduled?"
]

Input:
"What is the HOA's responsibility for the roof and how much will it cost to replace it?"

Output:
[
    "What is the HOA's responsibility for the roof and how much will it cost to replace it?"
]
User's question:
{question}
""".strip()

        response = self.llm_service.generate(prompt)
        print("\n========== RAW LLM RESPONSE ==========")
        print(repr(response))
        print("======================================")

        cleaned_response = response.strip()

        print("\n========== CLEANED RESPONSE ==========")
        print(repr(cleaned_response))
        print("======================================")
       
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        print("_+++++_____ Query Decomposer____")
        print(repr(cleaned_response))
        try:
            data = json.loads(cleaned_response)
           
        except json.JSONDecodeError as error:
            raise ValueError(
                "LLM returned invalid JSON during query decomposition."
            )from error
        if not isinstance(data,list):
            raise ValueError(
                "Query decomposition result must be a list."
            )
        if not all(isinstance(query,str)for query in data):
            raise ValueError(
                "Every decomposed query must be a string."
            )
        return data
        