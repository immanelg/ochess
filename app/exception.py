
class OchessException(Exception):
    pass

class ClientError(OchessException):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail
