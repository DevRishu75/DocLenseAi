from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user_model import User
from app.auth.dependecies import get_current_user
from app.schemas.agent_schemas import AgentRequest
from uuid import UUID
from app.agents.agents import Agent
from app.schemas.agent_schemas import AgentRequest,AgentResponse
from app.agents.tool_registry import ToolRegistry, ToolDefinition
from app.services.LLM_service import LLMService

from app.agent_tools.search_document import search_document
from app.agent_tools.retrieve_chunks import retrieve_chunks
from app.agent_tools.get_document import get_document



agent_router = APIRouter(
    prefix="/api/v1/agent",
    tags=["Agents"]
)

def create_tool_registry()->ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="search_document",
            description=("Search the user's document using semantic and keyword "
                "search. Use this when you need relevant information "
                "from the document."),
            parameters={
                "question":{
                    "type":"string",
                    "description":"The question or information to search for."
                }
            },
            function=search_document
        )
    )
    registry.register(
            ToolDefinition(
                name="get_document",
                description=( "Retrieve metadata and basic information about the "
                "current document."),
                parameters={},
                function=get_document
            )
        )
    registry.register(
        ToolDefinition(
            name="retrieve_chunks",
            description=( "Retrieve semantically relevant chunks from the current "
                "document."),
            parameters={
                "question": {
                    "type": "string",
                    "description": "The question used to retrieve relevant chunks."
                }
            },
            function=retrieve_chunks
        )
    )
    return registry
@agent_router.post("/{document_id}",response_model=AgentResponse)
async def run_agent(document_id:UUID,request:AgentRequest,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    tool_registry = create_tool_registry()
    agent = Agent(
        llm_service = LLMService(),
        tool_registry=tool_registry
    )
    state = agent.run(
        goal=request.goal,
        document_id=str(document_id),
        db=db,
        current_user=current_user
    )
    return AgentResponse(
        answer=state.final_answer or "",
        iteraton=state.iteration
    )

    