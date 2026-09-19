from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth_request import RegisterRequest,LoginRequest
from fastapi import APIRouter,Depends, HTTPException
from app.services.auth_service import AuthService

auth_router = APIRouter()

@auth_router.post("/api/v1/auth/register")
def register(
    data:RegisterRequest,
    db:Session=Depends(get_db)
):
    service = AuthService()
    user = service.register(
       data = data,
        db=db
    )
    return {
        "message":"User registered Successfully",
        "user_id": str(user.user_id),
        "email": user.email
    }
@auth_router.post("/api/v1/auth/login")
def login(
    data:LoginRequest,
    db:Session=Depends(get_db)
):
    service = AuthService()
    result = service.login(
        data = data,
        db = db
    )
    return result   #FastAPI serializes that Python dictionary into JSON and sends it back to the client.