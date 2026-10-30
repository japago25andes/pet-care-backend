from datetime import datetime
from decimal import Decimal
from typing import ClassVar

from pydantic import BaseModel, Field

from app.schemas.common import Actualizacion, CategoriaProducto, Salida, Texto20, Texto100, TextoLargo, Url


def _precio(descripcion: str, default=...):
    return Field(default, ge=0, max_digits=10, decimal_places=2, description=descripcion)


class ProductoCreate(BaseModel):
    nombre_producto: Texto100 = Field(examples=["Concentrado adulto 3 kg"])
    descripcion: TextoLargo | None = None
    categoria: CategoriaProducto | None = None
    precio_compra: Decimal = _precio("Costo para la veterinaria. Nunca se muestra al público")
    precio_venta: Decimal = _precio("Precio al público")
    stock: int = Field(0, ge=0)
    unidad_medida: Texto20 | None = Field(None, examples=["unidad"])
    imagen_url: Url | None = None


class ProductoUpdate(Actualizacion):
    campos_obligatorios: ClassVar[frozenset[str]] = frozenset({"nombre_producto", "precio_compra", "precio_venta", "stock"})

    nombre_producto: Texto100 | None = None
    descripcion: TextoLargo | None = None
    categoria: CategoriaProducto | None = None
    precio_compra: Decimal | None = _precio("Costo para la veterinaria", None)
    precio_venta: Decimal | None = _precio("Precio al público", None)
    stock: int | None = Field(None, ge=0)
    unidad_medida: Texto20 | None = None
    imagen_url: Url | None = None


class ProductoPublicoOut(Salida):
    id_producto: int
    id_veterinaria: int
    nombre_producto: str
    descripcion: str | None
    categoria: str | None
    precio_venta: float
    stock: int
    unidad_medida: str | None
    imagen_url: str | None


class ProductoOut(ProductoPublicoOut):
    """Vista para la veterinaria: incluye costo y estado."""

    precio_compra: float
    activo: bool
    fecha_creacion: datetime
