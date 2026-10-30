from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.carrito import CarritoCompras, DetalleCarrito
from app.models.veterinaria import Veterinaria


class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    id_veterinaria: Mapped[int] = mapped_column(ForeignKey("veterinarias.id_veterinaria"), nullable=False, index=True)
    id_carrito: Mapped[int] = mapped_column(ForeignKey("carrito_compras.id_carrito"), nullable=False, unique=True)
    fecha_pedido: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estado_pedido: Mapped[str] = mapped_column(String(30), server_default="pendiente")
    metodo_pago: Mapped[str | None] = mapped_column(String(30))
    direccion_entrega: Mapped[str] = mapped_column(Text, nullable=False)
    notas: Mapped[str | None] = mapped_column(Text)
    fecha_entrega: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    carrito: Mapped[CarritoCompras] = relationship()
    veterinaria: Mapped[Veterinaria] = relationship()

    @property
    def detalles(self) -> list[DetalleCarrito]:
        return self.carrito.detalles
