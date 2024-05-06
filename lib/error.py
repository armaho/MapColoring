class InvalidValueError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidConstraintError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
