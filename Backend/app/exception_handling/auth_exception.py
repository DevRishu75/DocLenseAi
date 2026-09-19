from app.exception_handling.base_exception import AppException

class AutherizationError(AppException):
    pass
class UserNotExistError(AppException):
    pass
class UserAlreadyExistError(AppException):
    pass
