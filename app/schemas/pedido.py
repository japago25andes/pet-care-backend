from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import EstadoPedido, MetodoPago, Salida, TextoLargo


class PedidoCreate(BaseModel):
    metodo_pago: MetodoPago
    direccion_entrega: TextoLargo | None = Field(None, description="Si se omite se usa la dirección del perfil")
    notas: TextoLargo | None = None


class PedidoEstadoUpdate(BaseModel):
    estado: EstadoPedido


class ItemPedidoOut(Salida):
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class PedidoOut(Salida):
    id_pedido: int
    id_usuario: int
    id_veterinaria: int
    id_carrito: int
    fecha_pedido: datetime
    total: float
    estado_pedido: str
    metodo_pago: str | None
    direccion_entrega: str
    notas: str | None
    fecha_entrega: datetime | None
    detalles: list[ItemPedidoOut]
