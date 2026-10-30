from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field

from app.schemas.common import Actualizacion, FechaHora, FrecuenciaRecordatorio, Salida, Texto100, TextoLargo, TipoRecordatorio


class RecordatorioCreate(BaseModel):
    titulo: Texto100 = Field(examples=["Desparasitación"])
    descripcion: TextoLargo | None = None
    tipo: TipoRecordatorio
    fecha_programada: FechaHora = Field(examples=["2026-11-15T09:00:00-05:00"])
    frecuencia: FrecuenciaRecordatorio | None = Field(None, description="Vacío o `unica` = no se repite")


class RecordatorioUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"titulo", "tipo", "fecha_programada"})

    titulo: Texto100 | None = None
    descripcion: TextoLargo | None = None
    tipo: TipoRecordatorio | None = None
    fecha_programada: FechaHora | None = Field(None, description="Si cambia, vuelve a quedar pendiente")
    frecuencia: FrecuenciaRecordatorio | None = None


class RecordatorioOut(Salida):
    id_recordatorio: int
    id_mascota: int
    titulo: str
    descripcion: str | None
    tipo: str
    fecha_programada: datetime
    frecuencia: str | None
    notificado: bool
    fecha_notificacion: datetime | None
    activo: bool
    fecha_creacion: datetime
