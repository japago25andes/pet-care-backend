from typing import ClassVar

from pydantic import BaseModel, Field

from app.schemas.common import Actualizacion, Correo, Salida, Texto20, Texto30, Texto50, Texto100


class ProfesionalCreate(BaseModel):
    nombre_completo: Texto100 = Field(examples=["Dra. Laura Gómez"])
    especialidad: Texto50 | None = Field(None, examples=["Medicina general"])
    numero_registro_profesional: Texto30 | None = Field(None, examples=["MV-12345"])
    telefono: Texto20 | None = None
    correo_electronico: Correo | None = None


class ProfesionalUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"nombre_completo"})

    nombre_completo: Texto100 | None = None
    especialidad: Texto50 | None = None
    numero_registro_profesional: Texto30 | None = None
    telefono: Texto20 | None = None
    correo_electronico: Correo | None = None


class ProfesionalOut(Salida):
    id_profesional: int
    id_veterinaria: int
    nombre_completo: str
    especialidad: str | None
    numero_registro_profesional: str | None
    telefono: str | None
    correo_electronico: str | None
    activo: bool
