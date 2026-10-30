from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, false, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mascota import Mascota


class Recordatorio(Base):
    __tablename__ = "recordatorios"

    id_recordatorio: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_mascota: Mapped[int] = mapped_column(ForeignKey("mascotas.id_mascota"), nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    fecha_programada: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    frecuencia: Mapped[str | None] = mapped_column(String(20))
    notificado: Mapped[bool] = mapped_column(Boolean, server_default=false())
    fecha_notificacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activo: Mapped[bool] = mapped_column(Boolean, server_default=true())
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    mascota: Mapped[Mascota] = relationship()
