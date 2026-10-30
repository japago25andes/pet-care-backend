from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import Conflict, NotFound
from app.crud.base import save
from app.crud.producto import get_producto_publico
from app.models.carrito import CarritoCompras, DetalleCarrito
from app.models.producto import Producto
from app.models.usuario import Usuario


def get_carrito_activo(db: Session, id_usuario: int) -> CarritoCompras | None:
    return db.scalar(
        select(CarritoCompras).where(CarritoCompras.id_usuario == id_usuario, CarritoCompras.estado == "activo")
    )


def get_or_create_carrito(db: Session, usuario: Usuario) -> CarritoCompras:
    carrito = get_carrito_activo(db, usuario.id_usuario)
    if carrito is None:
        carrito = save(db, CarritoCompras(id_usuario=usuario.id_usuario, estado="activo"))
    return carrito


def actualizar_linea(detalle: DetalleCarrito) -> None:
    """Toma el precio de venta actual del producto y recalcula el subtotal."""
    detalle.precio_unitario = detalle.producto.precio_venta
    detalle.subtotal = detalle.precio_unitario * detalle.cantidad


def sync_precios(db: Session, carrito: CarritoCompras) -> CarritoCompras:
    for detalle in carrito.detalles:
        actualizar_linea(detalle)
    return save(db, carrito)


def _validar_stock(producto: Producto, cantidad: int) -> None:
    if cantidad > producto.stock:
        raise Conflict(f"Stock insuficiente para '{producto.nombre_producto}' (disponible: {producto.stock})")


def get_detalle(carrito: CarritoCompras, id_detalle_carrito: int) -> DetalleCarrito:
    for detalle in carrito.detalles:
        if detalle.id_detalle_carrito == id_detalle_carrito:
            return detalle
    raise NotFound("Ese ítem no está en tu carrito")


def add_item(db: Session, carrito: CarritoCompras, id_producto: int, cantidad: int) -> CarritoCompras:
    producto = get_producto_publico(db, id_producto)
    if carrito.id_veterinaria not in (None, producto.id_veterinaria):
        raise Conflict("El carrito solo admite productos de una veterinaria. Vacíalo o haz el pedido primero")

    detalle = next((d for d in carrito.detalles if d.id_producto == id_producto), None)
    nueva_cantidad = cantidad + (detalle.cantidad if detalle else 0)
    _validar_stock(producto, nueva_cantidad)

    if detalle is None:
        detalle = DetalleCarrito(producto=producto, cantidad=nueva_cantidad)
        carrito.detalles.append(detalle)
    else:
        detalle.cantidad = nueva_cantidad
    return sync_precios(db, carrito)


def update_item(db: Session, carrito: CarritoCompras, id_detalle_carrito: int, cantidad: int) -> CarritoCompras:
    detalle = get_detalle(carrito, id_detalle_carrito)
    _validar_stock(detalle.producto, cantidad)
    detalle.cantidad = cantidad
    return sync_precios(db, carrito)


def remove_item(db: Session, carrito: CarritoCompras, id_detalle_carrito: int) -> CarritoCompras:
    carrito.detalles.remove(get_detalle(carrito, id_detalle_carrito))
    return sync_precios(db, carrito)


def vaciar(db: Session, carrito: CarritoCompras) -> CarritoCompras:
    carrito.detalles.clear()
    return save(db, carrito)
