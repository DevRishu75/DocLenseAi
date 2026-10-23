from datetime import datetime,timedelta,timezone
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError("SECRET_KEY must be configured with at least 32 bytes for HS256")
ALGORITHM = "HS256"
def create_access_token(user_id:str,expires_minutes:int=15)->str:
    expire = datetime.now(timezone.utc)+timedelta(minutes=expires_minutes)
    payload = {
        "sub": user_id,
        "type":"access",
        "exp":expire
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def create_refresh_token(user_id:str,expires_days:int=7)->str:
    expire = datetime.now(timezone.utc)+timedelta(days=expires_days)

    payload={
        "sub":user_id,
        "type":"refresh",
        "exp":expire
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
def decode_token(token:str)->dict:
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )