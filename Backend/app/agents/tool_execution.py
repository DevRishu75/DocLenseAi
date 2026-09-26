from typing import Any
from app.agents.tool_registry import ToolRegistry
from app.core.logging import logger

class ToolExecutor:
    def __init__(self,registry:ToolRegistry):
        self.registry = registry

    def execute(self,tool_name:str,arguments:dict[str,Any])->Any:
        tool = self.registry.get(tool_name)

        if tool is None:
            logger.exception("Agent could not get the answers")
            raise ValueError(
                f"Unknown tool:{tool_name}"
            )
        try:
            return tool.function(**arguments,)
        except TypeError as error:
            raise ValueError(
                f"Invalid argument for tool:{tool_name}"
            )from error
        
        