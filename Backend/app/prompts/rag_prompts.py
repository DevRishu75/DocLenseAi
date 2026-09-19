
def build_rag_prompt(context:str,question:str)->str:
   prompt = f"""

You answer questions about documents.

Use ONLY the DOCUMENT below.

If the answer cannot be found in the document, respond exactly:

I could not find this information in the document.

Do not guess.
Do not use outside knowledge.

DOCUMENT:
{context}

QUESTION:
{question}

ANSWER:
"""
   return prompt