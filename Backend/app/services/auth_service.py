from app.auth.password import hash_password,verify_password
from app.auth.jwt_token import create_access_token,create_refresh_token,decode_token
from sqlalchemy.orm import Session
from datetime import datetime,timezone
from app.models.user_model import User
from app.models.Session_model import RefreshToken
from app.schemas.auth_request import RegisterRequest,LoginRequest
from app.exception_handling.auth_exception import AutherizationError,UserAlreadyExistError,UserNotExistError
from app.auth.token_utils import hash_refresh_token

class AuthService:
    
    def register(self,data:RegisterRequest,db:Session):
        existing_user = (db.query(User).filter(User.email==data.email).first())

        if existing_user :
            raise UserAlreadyExistError(
                message="User Already Exist",
                status_code=400,
                error_code="USER_ALREADY_EXIST_ERROR"
            )

        #hash password
        hashed_password = hash_password(data.password)
        #create the user object
        user = User(
            email = data.email,
            password_hash = hashed_password
        )
        #add database to User table
        db.add(user)
        #commit the transaction
        db.commit()
        #refresh the table 
        db.refresh(user)
        return user

    def login(self,data:LoginRequest,db:Session):
        user = (db.query(User).filter(User.email==data.email).first())
        if not user:
            raise UserNotExistError(
                message="User Not exist",
                status_code=400,
                error_code="USER_NOT_EXIST_ERROR"
            )

        password_valid = verify_password(data.password,user.password_hash)

        if not password_valid:
            raise AutherizationError(
                message="Invalid Email or Password",
                status_code=401,
                error_code="AUTHERIZATION_ERROR"
            )

        access_token = create_access_token(str(user.user_id))
        refresh_token = create_refresh_token(str(user.user_id))
        payload = decode_token(refresh_token)
        expires_at = datetime.fromtimestamp(
            payload["exp"], tz=timezone.utc
        )
        token_hash = hash_refresh_token(refresh_token)
        refresh_token_record = RefreshToken(
            user_id = user.user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        db.add(refresh_token_record)
        db.commit()
        
        
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "type":"bearer"
        }
    