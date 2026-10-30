from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mascota import Mascota


class Vacuna(Base):
    __tablename__ = "vacunas"

    id_vacuna: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_mascota: Mapped[int] = mapped_column(ForeignKey("mascotas.id_mascota"), nullable=False, index=True)
    id_recordatorio: Mapped[int | None] = mapped_column(ForeignKey("recordatorios.id_recordatorio"))
    nombre_vacuna: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_aplicacion: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_proxima_dosis: Mapped[date | None] = mapped_column(Date)
    numero_dosis: Mapped[int] = mapped_column(Integer, server_default="1")
    lote: Mapped[str | None] = mapped_column(String(50))
    veterinario_nombre: Mapped[str | None] = mapped_column(String(100))
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    mascota: Mapped[Mascota] = relationship()
