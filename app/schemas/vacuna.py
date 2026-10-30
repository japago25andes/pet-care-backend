from datetime import date, datetime
from typing import ClassVar

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import Actualizacion, Salida, Texto50, Texto100


class VacunaCreate(BaseModel):
    nombre_vacuna: Texto100 = Field(examples=["Rabia"])
    fecha_aplicacion: date = Field(description="No puede ser futura", examples=["2026-10-01"])
    fecha_proxima_dosis: date | None = Field(None, description="Posterior a fecha_aplicacion", examples=["2027-10-01"])
    numero_dosis: int = Field(1, ge=1)
    lote: Texto50 | None = None
    veterinario_nombre: Texto100 | None = None
    id_recordatorio: int | None = Field(None, description="Recordatorio de la misma mascota")

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_aplicacion > date.today():
            raise ValueError("fecha_aplicacion no puede ser futura")
        if self.fecha_proxima_dosis and self.fecha_proxima_dosis <= self.fecha_aplicacion:
            raise ValueError("fecha_proxima_dosis debe ser posterior a fecha_aplicacion")
        return self


class VacunaUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"nombre_vacuna", "fecha_aplicacion", "numero_dosis"})

    nombre_vacuna: Texto100 | None = None
    fecha_aplicacion: date | None = None
    fecha_proxima_dosis: date | None = None
    numero_dosis: int | None = Field(None, ge=1)
    lote: Texto50 | None = None
    veterinario_nombre: Texto100 | None = None
    id_recordatorio: int | None = None


class VacunaOut(Salida):
    id_vacuna: int
    id_mascota: int
    id_recordatorio: int | None
    nombre_vacuna: str
    fecha_aplicacion: date
    fecha_proxima_dosis: date | None
    numero_dosis: int
    lote: str | None
    veterinario_nombre: str | None
    fecha_creacion: datetime
