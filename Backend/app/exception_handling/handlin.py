from fastapi import Request
from fastapi.responses import JSONResponse
from app.exception_handling.base_exception import AppException
import logging

logger = logging.getLogger(__name__)

async def app_exception_handler(
        request:Request,
        exc:AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code":exc.error_code,
            "message":exc.message
        }
    )
async def app_unexecpted_handler(
        request:Request,
        exc:Exception
):
    logger.exception(
        "Unexpected application error",
        extra={
            "method":request.method,
            "path":request.path
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "error_code":"INTERNAL_SERVER_ERROR",
            "message": "Unexcepted error occured"
        }
    )