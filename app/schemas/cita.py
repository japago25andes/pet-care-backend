from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field

from app.schemas.common import Actualizacion, EstadoCita, FechaHora, Salida, Texto200, TextoLargo


class CitaCreate(BaseModel):
    id_mascota: int = Field(examples=[1])
    id_profesional: int = Field(description="La veterinaria se toma del profesional", examples=[1])
    fecha_cita: FechaHora = Field(description="Debe ser futura. Sin zona horaria = UTC", examples=["2026-12-01T15:00:00-05:00"])
    motivo: Texto200 = Field(examples=["Control anual y vacunas"])


class CitaUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"fecha_cita", "motivo"})

    fecha_cita: FechaHora | None = Field(None, description="Si cambia, la cita vuelve a `programada`")
    motivo: Texto200 | None = None
    notas: TextoLargo | None = Field(None, description="Solo la veterinaria")


class CitaEstadoUpdate(BaseModel):
    estado: EstadoCita


class CitaOut(Salida):
    id_cita: int
    id_mascota: int
    id_profesional: int
    id_veterinaria: int
    fecha_cita: datetime
    motivo: str
    estado: str
    notas: str | None
    fecha_creacion: datetime
