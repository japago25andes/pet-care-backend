from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.veterinaria import Veterinaria


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_productos_stock_no_negativo"),
        CheckConstraint("precio_compra >= 0 AND precio_venta >= 0", name="ck_productos_precios_no_negativos"),
    )

    id_producto: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_veterinaria: Mapped[int] = mapped_column(ForeignKey("veterinarias.id_veterinaria"), nullable=False, index=True)
    nombre_producto: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria: Mapped[str | None] = mapped_column(String(30))
    precio_compra: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    unidad_medida: Mapped[str | None] = mapped_column(String(20))
    imagen_url: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, server_default=true())
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    veterinaria: Mapped[Veterinaria] = relationship()
