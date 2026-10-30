class APIError(Exception):
    """Error de negocio. main.py lo convierte en una respuesta JSON {"detail": ...}."""

    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class BadRequest(APIError):
    status_code = 400


class Forbidden(APIError):
    status_code = 403


class NotFound(APIError):
    status_code = 404


class Conflict(APIError):
    status_code = 409
