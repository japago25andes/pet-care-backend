from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.usuario import Usuario


class Mensaje(Base):
    __tablename__ = "mensajes"

    id_mensaje: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_usuario_remitente: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    id_usuario_destinatario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    id_veterinaria: Mapped[int | None] = mapped_column(ForeignKey("veterinarias.id_veterinaria"))
    id_cita: Mapped[int | None] = mapped_column(ForeignKey("citas_veterinarias.id_cita"))
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    leido: Mapped[bool] = mapped_column(Boolean, server_default=false())
    fecha_envio: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    remitente: Mapped[Usuario] = relationship(foreign_keys=[id_usuario_remitente])
    destinatario: Mapped[Usuario] = relationship(foreign_keys=[id_usuario_destinatario])

    @property
    def nombre_remitente(self) -> str:
        return self.remitente.nombre_completo

    @property
    def nombre_destinatario(self) -> str:
        return self.destinatario.nombre_completo
