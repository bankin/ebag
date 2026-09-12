class NotFoundError(Exception):
    def __init__(self, message: str = "Not found"):
        self.message = message
        super().__init__(message)


class NameConflictError(Exception):
    def __init__(self, message: str = "Name already exists"):
        self.message = message
        super().__init__(message)