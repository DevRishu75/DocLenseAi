from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.refresh_request import RefreshTokenRequest
from app.models.Session_model import RefreshToken
from app.auth.token_utils import hash_refresh_token


logout_router = APIRouter()
@logout_router.post('/api/v1/logout')
def logout(token:RefreshTokenRequest,db:Session=Depends(get_db)):
    hash_token = hash_refresh_token(token)
    session = db.query(RefreshToken).filter(RefreshToken.token_hash == hash_token).first()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    session.revoked = True
    db.commit()
    return{
        "message": "Logged out Successfully "
    }