from dataclasses import dataclass
from typing import Callable,Any

@dataclass
class ToolDefinition:
    name:str
    description:str
    parameters:dict[str,Any]
    function:callable

class ToolRegistry:
    def __init__(self):
        self._tools : dict[str,ToolDefinition]= {}
    def register(self,tool:ToolDefinition):
        self._tools[tool.name]=tool
    def get(self,tool_name)->ToolDefinition|None:
        self._tools.get(tool_name)
    def get_all(self)->list[ToolDefinition]:
        return list(self._tools.values())
    def get_tool_description(self,tool)->list[dict[str,Any]]:
        return[
            {
            "name":tool.name,
            "description":tool.description,
            "parameters":tool.parameters
        }
        for tool in self._tools.values()
        ]
    
