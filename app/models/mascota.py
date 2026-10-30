from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Mascota(Base):
    __tablename__ = "mascotas"
    __table_args__ = (
        # El chip es único solo entre mascotas activas: al desactivar una mascota su chip queda libre.
        Index("uq_mascotas_numero_chip_activo", "numero_chip", unique=True, postgresql_where=text("activo")),
    )

    id_mascota: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    especie: Mapped[str] = mapped_column(String(30), nullable=False)
    raza: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sexo: Mapped[str | None] = mapped_column(String(10), nullable=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    peso_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    color_mascota: Mapped[str | None] = mapped_column(String(30), nullable=True)
    numero_chip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    foto_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    alergias: Mapped[str | None] = mapped_column(Text, nullable=True)
    condiciones_medicas: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
