class UserAlreadyExistsException(Exception):
    pass

class UserNotFoundException(Exception):
    pass

class DatabaseConnectionException(Exception):
    pass

class ProductNotFoundException(Exception):
    pass

class NotFoundException(Exception):
    pass

class UnauthorizedException(Exception):
    pass