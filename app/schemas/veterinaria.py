from typing import ClassVar

from pydantic import BaseModel, Field

from app.schemas.common import Actualizacion, Correo, Salida, Texto20, Texto100, TextoLargo


class VeterinariaCreate(BaseModel):
    nombre_comercial: Texto100 = Field(examples=["Clínica Patitas"])
    direccion: TextoLargo = Field(examples=["Av. 68 # 12-34, Bogotá"])
    telefono: Texto20 = Field(examples=["6015551234"])
    correo_electronico: Correo | None = Field(None, examples=["contacto@patitas.com"])
    horario_atencion: Texto100 | None = Field(None, examples=["Lun-Sáb 8:00-18:00"])
    latitud: float | None = Field(None, ge=-90, le=90, examples=[4.6482837])
    longitud: float | None = Field(None, ge=-180, le=180, examples=[-74.0939946])


class VeterinariaUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"nombre_comercial", "direccion", "telefono", "activo"})

    nombre_comercial: Texto100 | None = None
    direccion: TextoLargo | None = None
    telefono: Texto20 | None = None
    correo_electronico: Correo | None = None
    horario_atencion: Texto100 | None = None
    latitud: float | None = Field(None, ge=-90, le=90)
    longitud: float | None = Field(None, ge=-180, le=180)
    activo: bool | None = Field(None, description="Solo un admin puede cambiarlo (reactivar una veterinaria)")


class VeterinariaOut(Salida):
    id_veterinaria: int
    id_usuario: int
    nombre_comercial: str
    direccion: str
    telefono: str
    correo_electronico: str | None
    horario_atencion: str | None
    latitud: float | None
    longitud: float | None
    calificacion_promedio: float
    activo: bool
    distancia_km: float | None = Field(None, description="Solo en búsquedas con lat/lng")
