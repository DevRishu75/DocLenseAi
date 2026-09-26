from dataclasses import dataclass,field
from typing import Any

@dataclass
class AgentState:
    goal:str
    messages:list[dict[str,Any]]=field(default_factory=list)
    tool_result:list[dict[str,Any]]=field(default_factory=list)
    iteration:int=0
    final_answer:str|None=None
    finished:bool=False