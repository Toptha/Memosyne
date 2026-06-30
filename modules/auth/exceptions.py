class ValidationException(Exception):
    pass


class InvalidUsernameException(ValidationException):
    pass


class InvalidEmailException(ValidationException):
    pass


class WeakPasswordException(ValidationException):
    pass


class PasswordMismatchException(ValidationException):
    pass


class UserAlreadyExistsException(ValidationException):
    pass


class InvalidLoginException(ValidationException):
    pass