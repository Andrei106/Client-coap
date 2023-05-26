from exception.ExceptionBase import ExceptionBase


class UserInterfaceException(ExceptionBase):
    def __init__(self, message):
        super().__init__(message)

