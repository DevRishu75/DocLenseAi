from app.services.LLM_service import LLMService
from app.agents.state import AgentState
from app.agents.tool_execution import ToolExecutor
from app.agents.tool_registry import ToolRegistry
from app.agents.decision_parser import DecisionParser
from app.prompts.agent_prompts import build_agent_prompt
from sqlalchemy.orm import Session
from app.models.user_model import User


class Agent:

    MAX_ITERATION = 5
    def __init__(self,llm_service:LLMService,tool_registry:ToolRegistry):
        self.llm_service = llm_service
        self.tool_registry = tool_registry
        self.tool_executor = ToolExecutor(tool_registry)
        self.decision_parser = DecisionParser()
    def run(self,goal:str,document_id:str,db:Session,current_user:User)->AgentState:
        state = AgentState(
            goal=goal
        )
        while not state.finished:
            if state.iteration>=self.MAX_ITERATION:
                state.final_answer=(
                    "The agent reached the maximum number of steps allowed"
                )
                state.finished = True
                break
            state.iteration+=1
            prompt = build_agent_prompt(goal=state.goal,tools=self.tool_registry.get_tool_description(),history=state.messages)
            llm_response = self.llm_service.generate(prompt)
            decision = self.decision_parser.parse(llm_response)
            if decision.action=="final_answer":
                state.final_answer=(
                    decision.final_answer or "The agent completed without an answer"
                )
                state.finished=True
                break
            tool = self.tool_registry.get(decision.action)
            if tool is None:
                raise ValueError(
                    f"Agent selected an unknown tool {decision.action}"
                )
            tool_arguments = {
                **decision.arguments,
                "document_id":str(document_id),
                "db":db,
                "current_user":current_user
            }
            result = self.tool_executor.execute(
                tool_name=decision.action,
                arguments=tool_arguments
            )
            state.tool_result.append(result)
            state.messages.append(
                {
                    "role":"tool",
                    "tool":decision.action,
                    "content":str(result)
                }
            )
        return state
            