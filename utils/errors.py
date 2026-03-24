class AppError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(message)  # This is my own error, every error has 1)message 2) HTTP status code


class ValidationError(AppError):
    def __init__(self, message="Invalid input"):
        super().__init__(message, 400)


class NotFoundError(AppError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)


class ForbiddenError(AppError):
    def __init__(self, message="Access denied"):
        super().__init__(message, 403)

