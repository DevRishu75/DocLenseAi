from pydantic import BaseModel,Field

class AgentRequest(BaseModel):
    goal:str=Field(
        ...,
        min_length=1,
        max_length=5000
    ),

class AgentResponse(BaseModel):
    answer:str
    iteration:int
    
