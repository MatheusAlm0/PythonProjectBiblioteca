class APIException(Exception):
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class BadRequestException(APIException):
    def __init__(self, message):
        super().__init__(message, 400)

class UnauthorizedException(APIException):
    def __init__(self, message):
        super().__init__(message, 401)

class PaymentRequiredException(APIException):
    def __init__(self, message):
        super().__init__(message, 402)

class RateLimitException(APIException):
    def __init__(self, message):
        super().__init__(message, 429)