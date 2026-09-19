from fastapi import FastAPI
from app.api.routes.upload import upload_router
from app.api.routes.document import document_router
from app.api.routes.auth_router import auth_router
from app.api.routes.query import ask_router
from app.api.routes.session_router import refresh_router
from app.api.routes.logout import logout_router
from app.db.init_db import init_db
from app.exception_handling.base_exception import AppException
from app.exception_handling.handlin import app_exception_handler,app_unexecpted_handler
from app.core.logging import setup_logging
from app.middleware.request_logging import request_logging_middleware
from fastapi.middleware.cors import CORSMiddleware

setup_logging()
app = FastAPI(
    title = "DOCUMIND AI",
    description = "AI powered Docuement Intelligence Engine",
    version = '1.0.0'
)
app.middleware('http')(request_logging_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origin=[
         "http://localhost:8000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_method=["*"],
    allow_hearder=["*"]
)
app.add_exception_handler(
    AppException,
    app_exception_handler,
)
app.add_exception_handler(
    Exception,
    app_unexecpted_handler
)
init_db()

@app.get("/")
def root():
    return{
        "message": "Welcome to DOCUMIND AI ",
        "Success": 200
    }
# print(upload_router.routes)
# for route in app.routes:
#     print(route.path, route.methods)
app.include_router(upload_router)
app.include_router(document_router)
app.include_router(auth_router)
app.include_router(ask_router)
app.include_router(refresh_router)
app.include_router(logout_router)