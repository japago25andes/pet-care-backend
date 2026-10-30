from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Veterinaria(Base):
    __tablename__ = "veterinarias"

    id_veterinaria: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Usuario responsable (rol "veterinaria"). No estaba en el ER: sin él nadie podría gestionarla.
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    nombre_comercial: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion: Mapped[str] = mapped_column(Text, nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    correo_electronico: Mapped[str | None] = mapped_column(String(100))
    horario_atencion: Mapped[str | None] = mapped_column(String(100))
    latitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 8))
    longitud: Mapped[Decimal | None] = mapped_column(Numeric(11, 8))
    calificacion_promedio: Mapped[Decimal] = mapped_column(Numeric(3, 2), server_default="0")
    activo: Mapped[bool] = mapped_column(Boolean, server_default=true())
