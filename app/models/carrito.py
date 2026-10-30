from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.producto import Producto


class DetalleCarrito(Base):
    __tablename__ = "detalle_carrito"
    __table_args__ = (
        UniqueConstraint("id_carrito", "id_producto", name="uq_detalle_carrito_producto"),
        CheckConstraint("cantidad > 0", name="ck_detalle_carrito_cantidad_positiva"),
    )

    id_detalle_carrito: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_carrito: Mapped[int] = mapped_column(ForeignKey("carrito_compras.id_carrito"), nullable=False, index=True)
    id_producto: Mapped[int] = mapped_column(ForeignKey("productos.id_producto"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    producto: Mapped[Producto] = relationship()

    @property
    def nombre_producto(self) -> str:
        return self.producto.nombre_producto

    @property
    def disponible(self) -> bool:
        producto = self.producto
        return producto.activo and producto.veterinaria.activo and producto.stock >= self.cantidad


class CarritoCompras(Base):
    __tablename__ = "carrito_compras"
    __table_args__ = (
        # Cada usuario tiene como máximo un carrito activo.
        Index(
            "uq_carrito_activo_por_usuario",
            "id_usuario",
            unique=True,
            postgresql_where=text("estado = 'activo'"),
        ),
    )

    id_carrito: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    estado: Mapped[str] = mapped_column(String(20), server_default="activo")

    detalles: Mapped[list[DetalleCarrito]] = relationship(
        cascade="all, delete-orphan", order_by=DetalleCarrito.id_detalle_carrito
    )

    @property
    def id_veterinaria(self) -> int | None:
        """Un carrito solo contiene productos de una veterinaria."""
        return self.detalles[0].producto.id_veterinaria if self.detalles else None

    @property
    def total(self) -> Decimal:
        return sum((detalle.subtotal for detalle in self.detalles), Decimal("0"))
