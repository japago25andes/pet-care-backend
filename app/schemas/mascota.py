from datetime import date
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import Actualizacion, Salida, SexoMascota, Texto30, Texto50, TextoLargo, Url


def _peso():
    return Field(None, gt=0, le=999.99, description="Kilogramos, máximo 2 decimales", examples=[12.5])


def _no_futura(valor: date | None) -> date | None:
    if valor is not None and valor > date.today():
        raise ValueError("La fecha de nacimiento no puede ser futura")
    return valor


class MascotaCreate(BaseModel):
    nombre: Texto50 = Field(examples=["Luna"])
    especie: Texto30 = Field(examples=["perro"])
    raza: Texto50 | None = Field(None, examples=["Labrador"])
    sexo: SexoMascota | None = None
    fecha_nacimiento: date | None = Field(None, examples=["2021-05-10"])
    peso_kg: float | None = _peso()
    color_mascota: Texto30 | None = Field(None, examples=["dorado"])
    numero_chip: Texto50 | None = Field(None, description="Único entre mascotas activas", examples=["985141000123456"])
    foto_url: Url | None = None
    alergias: TextoLargo | None = None
    condiciones_medicas: TextoLargo | None = None

    validar_nacimiento = field_validator("fecha_nacimiento")(_no_futura)


class MascotaUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"nombre", "especie"})

    nombre: Texto50 | None = None
    especie: Texto30 | None = None
    raza: Texto50 | None = None
    sexo: SexoMascota | None = None
    fecha_nacimiento: date | None = None
    peso_kg: float | None = _peso()
    color_mascota: Texto30 | None = None
    numero_chip: Texto50 | None = None
    foto_url: Url | None = None
    alergias: TextoLargo | None = None
    condiciones_medicas: TextoLargo | None = None

    validar_nacimiento = field_validator("fecha_nacimiento")(_no_futura)


class MascotaOut(Salida):
    id_mascota: int
    id_usuario: int
    nombre: str
    especie: str
    raza: str | None
    sexo: str | None
    fecha_nacimiento: date | None
    peso_kg: float | None
    color_mascota: str | None
    numero_chip: str | None
    foto_url: str | None
    alergias: str | None
    condiciones_medicas: str | None
    activo: bool
