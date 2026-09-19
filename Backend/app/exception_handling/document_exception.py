from app.exception_handling.base_exception import AppException
class DocumentNotFoundError(AppException):
    pass
class DocumentProcessingError(AppException):
    pass
