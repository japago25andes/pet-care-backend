from datetime import datetime, timezone
from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, StringConstraints, model_validator


def _texto(max_length: int):
    return Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=max_length)]


Texto20 = _texto(20)
Texto30 = _texto(30)
Texto50 = _texto(50)
Texto100 = _texto(100)
Texto200 = _texto(200)
TextoLargo = _texto(5000)


def _validar_url(valor: str) -> str:
    if not valor.startswith(("http://", "https://")):
        raise ValueError("Debe empezar por http:// o https://")
    return valor


Url = Annotated[str, StringConstraints(strip_whitespace=True, max_length=2048), AfterValidator(_validar_url)]


def _normalizar_correo(valor: str) -> str:
    if len(valor) > 100:
        raise ValueError("Máximo 100 caracteres")
    return valor.lower()


# El correo se guarda siempre en minúsculas.
Correo = Annotated[EmailStr, AfterValidator(_normalizar_correo)]


def _a_utc(valor: datetime) -> datetime:
    return valor.replace(tzinfo=timezone.utc) if valor.tzinfo is None else valor


# Fecha y hora; si llega sin zona horaria se interpreta como UTC.
FechaHora = Annotated[datetime, AfterValidator(_a_utc)]

RolUsuario = Literal["cliente", "veterinaria", "admin"]
SexoMascota = Literal["macho", "hembra"]
EstadoCita = Literal["programada", "confirmada", "completada", "cancelada", "no_asistio"]
TipoRecordatorio = Literal["vacuna", "medicamento", "desparasitacion", "cita", "higiene", "alimentacion", "otro"]
FrecuenciaRecordatorio = Literal["unica", "diaria", "semanal", "mensual", "anual"]
CategoriaProducto = Literal["alimento", "medicamento", "accesorio", "higiene", "juguete", "otro"]
EstadoPedido = Literal["pendiente", "confirmado", "enviado", "entregado", "cancelado"]
MetodoPago = Literal["efectivo", "tarjeta", "transferencia"]


class Salida(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Actualizacion(BaseModel):
    """Base de los PATCH: solo se modifican los campos enviados; los obligatorios no aceptan null."""

    campos_obligatorios: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def _rechazar_nulos(self):
        nulos = sorted(c for c in self.model_fields_set & self.campos_obligatorios if getattr(self, c) is None)
        if nulos:
            raise ValueError(f"Estos campos no pueden ser null: {', '.join(nulos)}")
        return self

    def cambios(self) -> dict:
        return self.model_dump(exclude_unset=True)


class ErrorOut(BaseModel):
    detail: str


class ConteoOut(BaseModel):
    total: int
