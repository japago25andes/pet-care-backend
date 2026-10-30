from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import Salida, TextoLargo


class MensajeCreate(BaseModel):
    id_usuario_destinatario: int = Field(examples=[2])
    contenido: TextoLargo = Field(examples=["Hola, ¿tienen disponibilidad el sábado?"])
    id_veterinaria: int | None = Field(None, description="Veterinaria sobre la que trata el mensaje")
    id_cita: int | None = Field(None, description="Cita relacionada; debes ser parte de ella")


class MensajeOut(Salida):
    id_mensaje: int
    id_usuario_remitente: int
    nombre_remitente: str
    id_usuario_destinatario: int
    nombre_destinatario: str
    id_veterinaria: int | None
    id_cita: int | None
    contenido: str
    leido: bool
    fecha_envio: datetime
