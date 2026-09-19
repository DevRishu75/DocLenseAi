from fastapi import APIRouter,Depends,HTTPException,status
from app.schemas.query_response import QueryRequest,QueryResponse
from app.services.query_service import QueryService
from app.models.user_model import User
from app.auth.dependecies import get_current_user
from uuid import UUID
from app.db.session import get_db
from sqlalchemy.orm import Session
ask_router = APIRouter()

@ask_router.post('/api/v1/ask/{document_id}',response_model=QueryResponse)
async def ask_query(document_id:UUID,request:QueryRequest,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    query_service = QueryService()
    result = query_service.ask(request.question,document_id,db,current_user)
    return result