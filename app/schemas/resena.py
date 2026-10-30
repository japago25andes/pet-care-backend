from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field

from app.schemas.common import Actualizacion, Salida, TextoLargo


class ResenaCreate(BaseModel):
    calificacion: int = Field(ge=1, le=5, examples=[5])
    comentario: TextoLargo | None = Field(None, examples=["Excelente atención"])
    id_pedido: int | None = Field(None, description="Pedido propio y entregado de esta veterinaria (opcional)")


class ResenaUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"calificacion"})

    calificacion: int | None = Field(None, ge=1, le=5)
    comentario: TextoLargo | None = None


class ResenaOut(Salida):
    id_resena: int
    id_usuario: int
    nombre_usuario: str
    id_veterinaria: int
    id_pedido: int | None
    calificacion: int
    comentario: str | None
    fecha_creacion: datetime
