from datetime import datetime
from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, BaseModel, Field, StringConstraints

from app.schemas.common import Actualizacion, Correo, RolUsuario, Salida, Texto20, Texto100, TextoLargo


def _max_72_bytes(valor: str) -> str:
    # bcrypt solo usa los primeros 72 bytes
    if len(valor.encode()) > 72:
        raise ValueError("La contraseña no puede superar 72 bytes")
    return valor


Contrasena = Annotated[str, StringConstraints(min_length=8, max_length=72), AfterValidator(_max_72_bytes)]


class UsuarioCreate(BaseModel):
    nombre_completo: Texto100 = Field(examples=["Ana Pérez"])
    correo_electronico: Correo = Field(examples=["ana@correo.com"])
    contrasena: Contrasena = Field(examples=["Secreta123"])
    telefono: Texto20 | None = Field(None, examples=["3001234567"])
    direccion: TextoLargo | None = Field(None, examples=["Calle 10 # 20-30, Bogotá"])
    rol: Literal["cliente", "veterinaria"] = Field(
        "cliente",
        description="`veterinaria` puede registrar y gestionar veterinarias. `admin` solo se asigna por script.",
    )


class UsuarioUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"nombre_completo"})

    nombre_completo: Texto100 | None = None
    telefono: Texto20 | None = None
    direccion: TextoLargo | None = None


class CambioContrasena(BaseModel):
    contrasena_actual: str = Field(examples=["Secreta123"])
    contrasena_nueva: Contrasena = Field(examples=["NuevaClave456"])


class UsuarioAdminUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"rol", "activo"})

    rol: RolUsuario | None = None
    activo: bool | None = None


class UsuarioOut(Salida):
    id_usuario: int
    nombre_completo: str
    correo_electronico: str
    telefono: str | None
    direccion: str | None
    rol: str
    activo: bool
    fecha_registro: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
