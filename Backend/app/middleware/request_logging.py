import logging
import time
import uuid
from fastapi import Request

logger = logging.getLogger(__name__)

async def request_logging_middleware(request:Request,call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Request Failed",
            extra={
                "request_id":request_id,
                "method":request.method,
                "Path":request.url.path
            }
        )
        raise
    duration = time.perf_counter()-start_time
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request Completed",
        extra={
            "request_id":request_id,
            "method":request.method,
            "path":request.url.path,
            "status_code":response.status_code,
            "duration_ms":round(duration *1000,2)
        }
    )
    return response