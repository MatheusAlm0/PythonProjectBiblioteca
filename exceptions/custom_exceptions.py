class APIException(Exception):
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class BadRequestException(APIException):
    def __init__(self, message):
        super().__init__(message, status_code=400)

class PaymentRequiredException(APIException):
    def __init__(self, message):
        super().__init__(message, status_code=402)

class UnauthorizedException(APIException):
    def __init__(self, message):
        super().__init__(message, status_code=401)

class RateLimitException(APIException):
    def __init__(self, message):
        super().__init__(message, status_code=429)
