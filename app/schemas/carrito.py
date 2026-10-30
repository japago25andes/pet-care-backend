from pydantic import BaseModel, Field

from app.schemas.common import Salida


class ItemCarritoCreate(BaseModel):
    id_producto: int = Field(examples=[1])
    cantidad: int = Field(1, ge=1, le=999, description="Se suma si el producto ya está en el carrito")


class ItemCarritoUpdate(BaseModel):
    cantidad: int = Field(ge=1, le=999, description="Cantidad final de la línea")


class DetalleCarritoOut(Salida):
    id_detalle_carrito: int
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float
    disponible: bool = Field(description="False si el producto se desactivó o ya no hay stock suficiente")


class CarritoOut(Salida):
    id_carrito: int
    estado: str
    id_veterinaria: int | None = Field(description="Veterinaria de los productos (una por carrito)")
    detalles: list[DetalleCarritoOut]
    total: float
