from fastapi import APIRouter,HTTPException,status,Depends
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.auth.jwt_token import create_refresh_token,decode_token,create_access_token
from app.schemas.refresh_request import RefreshTokenRequest
from app.models.Session_model import RefreshToken
from app.auth.token_utils import hash_refresh_token
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timezone

refresh_router = APIRouter()

@refresh_router.post("/api/v1/refresh")
def refresh(token:RefreshTokenRequest,db:Session=Depends(get_db)):
    try:
        payload = decode_token(token.refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    if payload is None:
        return None
    if payload["type"] != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access denied"
        )
    user_id = payload["sub"]
    hash_token = hash_refresh_token(token.refresh_token)
    session = db.query(RefreshToken).filter(RefreshToken.token_hash == str(hash_token)).first()
    if session is None:
        return None
    if session.revoked == True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unathorized access denied"
        )
    if session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has Expired"
        )
    #old refresh token is not usable now
    session.revoked = True
    # create new refresh token 
    new_refresh_token = create_refresh_token(user_id)
    #decode token to get payload --
    new_payload = decode_token(new_refresh_token)

    # get access of expire from payload-- 
    new_expires_at = datetime.fromtimestamp(
        new_payload["exp"],
        tz=timezone.utc
    )
    # hash token -- 
    new_hash_token = hash_refresh_token(new_refresh_token)
    #putting the new expires token inside the database 
    new_session = RefreshToken(
        user_id = user_id,
        token_hash = new_hash_token,
        expires_at = new_expires_at
    )
    db.add(new_session)
    db.commit()

    new_access_token = create_access_token(user_id)
    return {
        "access_token":new_access_token,
        "refresh_token": new_refresh_token,
        "type":"bearer"
    }
