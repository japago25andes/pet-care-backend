from app.schemas.common import ErrorOut

_DESCRIPCIONES = {
    400: "Datos válidos pero no aplicables a la operación",
    401: "No autenticado: token ausente, inválido o vencido",
    403: "Sin permisos para esta acción",
    404: "Recurso no encontrado (o no tienes acceso a él)",
    409: "Conflicto: dato duplicado, sin stock o estado que no lo permite",
}


def errores(*codigos: int) -> dict:
    """Documenta en Swagger las respuestas de error de un endpoint."""
    return {codigo: {"model": ErrorOut, "description": _DESCRIPCIONES[codigo]} for codigo in codigos}
