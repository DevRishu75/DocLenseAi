from fastapi import APIRouter, UploadFile, File,Depends
from app.services.file_service import FileService
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user_model import User
from app.auth.dependecies import get_current_user

upload_router = APIRouter()

@upload_router.post('/api/v1/uploads')
def upload(file: UploadFile = File(...),
           db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    service = FileService()
    return service.process_pdf(file,db,current_user)

 