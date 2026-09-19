from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    question:str

class SourceResponse(BaseModel):
    chunk_id:str
    chunk_index:Optional[int]=None
    source:Optional[str]=None
    relevance_score:float

class QueryResponse(BaseModel):
    answer:str
    sources:list[SourceResponse]