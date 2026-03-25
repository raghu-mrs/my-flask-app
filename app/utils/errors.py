class AppError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ValidationError(AppError):
    def __init__(self, message="Invalid input"):
        super().__init__(message, 400)

class UnauthorizedError(AppError):
    def __init__(self, message="Unauthorized access"):
        super().__init__(message, 401)

class ForbiddenError(AppError):
    def __init__(self, message="Access denied"):
        super().__init__(message, 403)

class NotFoundError(AppError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)

class InternalServerError(AppError):
    def __init__(self, message="Internal server error"):
        super().__init__(message, 500)
