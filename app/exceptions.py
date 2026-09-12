class NotFoundError(Exception):
    def __init__(self, message: str = "Not found"):
        self.message = message
        super().__init__(message)


class NameConflictError(Exception):
    def __init__(self, message: str = "Name already exists"):
        self.message = message
        super().__init__(message)


class ConflictError(Exception):
    def __init__(self, message: str = "Conflict"):
        self.message = message
        super().__init__(message)


class InvalidImageError(Exception):
    def __init__(self, message: str = "Invalid image"):
        self.message = message
        super().__init__(message)