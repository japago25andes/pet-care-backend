from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mascota import Mascota


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id_medicamento: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_mascota: Mapped[int] = mapped_column(ForeignKey("mascotas.id_mascota"), nullable=False, index=True)
    id_recordatorio: Mapped[int | None] = mapped_column(ForeignKey("recordatorios.id_recordatorio"))
    nombre_medicamento: Mapped[str] = mapped_column(String(100), nullable=False)
    dosis: Mapped[str | None] = mapped_column(String(50))
    unidad_medida: Mapped[str | None] = mapped_column(String(20))
    frecuencia_administracion: Mapped[str | None] = mapped_column(String(50))
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date | None] = mapped_column(Date)
    observaciones: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, server_default=true())

    mascota: Mapped[Mascota] = relationship()
