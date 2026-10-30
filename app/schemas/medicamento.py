from datetime import date
from typing import ClassVar

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import Actualizacion, Salida, Texto20, Texto50, Texto100, TextoLargo


class MedicamentoCreate(BaseModel):
    nombre_medicamento: Texto100 = Field(examples=["Amoxicilina"])
    dosis: Texto50 | None = Field(None, examples=["250"])
    unidad_medida: Texto20 | None = Field(None, examples=["mg"])
    frecuencia_administracion: Texto50 | None = Field(None, examples=["Cada 12 horas"])
    fecha_inicio: date = Field(examples=["2026-11-01"])
    fecha_fin: date | None = Field(None, examples=["2026-11-10"])
    observaciones: TextoLargo | None = None
    id_recordatorio: int | None = Field(None, description="Recordatorio de la misma mascota")

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin no puede ser anterior a fecha_inicio")
        return self


class MedicamentoUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"nombre_medicamento", "fecha_inicio"})

    nombre_medicamento: Texto100 | None = None
    dosis: Texto50 | None = None
    unidad_medida: Texto20 | None = None
    frecuencia_administracion: Texto50 | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    observaciones: TextoLargo | None = None
    id_recordatorio: int | None = None


class MedicamentoOut(Salida):
    id_medicamento: int
    id_mascota: int
    id_recordatorio: int | None
    nombre_medicamento: str
    dosis: str | None
    unidad_medida: str | None
    frecuencia_administracion: str | None
    fecha_inicio: date
    fecha_fin: date | None
    observaciones: str | None
    activo: bool
