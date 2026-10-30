from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.core.errors import BadRequest, Conflict, Forbidden, NotFound
from app.core.permissions import is_admin
from app.crud.base import paginate, save
from app.crud.carrito import actualizar_linea, get_carrito_activo
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.models.veterinaria import Veterinaria
from app.schemas.pedido import PedidoCreate

TRANSICIONES = {
    "pendiente": {"confirmado", "cancelado"},
    "confirmado": {"enviado", "cancelado"},
    "enviado": {"entregado"},
}


def es_veterinaria(pedido: Pedido, usuario: Usuario) -> bool:
    return is_admin(usuario) or pedido.veterinaria.id_usuario == usuario.id_usuario


def get_pedido_accesible(db: Session, id_pedido: int, usuario: Usuario) -> Pedido:
    """Pedido del comprador o de la veterinaria que lo atiende."""
    pedido = db.get(Pedido, id_pedido)
    if pedido is None or not (pedido.id_usuario == usuario.id_usuario or es_veterinaria(pedido, usuario)):
        raise NotFound("Pedido no encontrado")
    return pedido


def _bloquear_productos(db: Session, ids: list[int]) -> dict[int, Producto]:
    """SELECT ... FOR UPDATE: evita vender el mismo stock en dos pedidos simultáneos."""
    stmt = (
        select(Producto)
        .where(Producto.id_producto.in_(ids))
        .order_by(Producto.id_producto)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    return {producto.id_producto: producto for producto in db.scalars(stmt)}


def create_pedido(db: Session, usuario: Usuario, pedido_in: PedidoCreate) -> Pedido:
    carrito = get_carrito_activo(db, usuario.id_usuario)
    if carrito is None or not carrito.detalles:
        raise BadRequest("El carrito está vacío")
    direccion = pedido_in.direccion_entrega or usuario.direccion
    if not direccion:
        raise BadRequest("Indica direccion_entrega o guarda una dirección en tu perfil")

    productos = _bloquear_productos(db, [d.id_producto for d in carrito.detalles])
    for detalle in carrito.detalles:
        producto = productos[detalle.id_producto]
        if not producto.activo or not producto.veterinaria.activo:
            raise Conflict(f"'{producto.nombre_producto}' ya no está disponible. Quítalo del carrito")
        if producto.stock < detalle.cantidad:
            raise Conflict(f"Stock insuficiente para '{producto.nombre_producto}' (disponible: {producto.stock})")

    for detalle in carrito.detalles:
        productos[detalle.id_producto].stock -= detalle.cantidad
        actualizar_linea(detalle)

    pedido = Pedido(
        id_usuario=usuario.id_usuario,
        id_veterinaria=carrito.id_veterinaria,
        id_carrito=carrito.id_carrito,
        total=carrito.total,
        estado_pedido="pendiente",
        metodo_pago=pedido_in.metodo_pago,
        direccion_entrega=direccion,
        notas=pedido_in.notas,
    )
    carrito.estado = "convertido"
    return save(db, pedido)


def list_pedidos(db: Session, usuario: Usuario, page: Pagination, estado: str | None = None) -> list[Pedido]:
    stmt = (
        select(Pedido)
        .join(Veterinaria, Pedido.id_veterinaria == Veterinaria.id_veterinaria)
        .order_by(Pedido.fecha_pedido.desc())
    )
    if not is_admin(usuario):
        stmt = stmt.where(or_(Pedido.id_usuario == usuario.id_usuario, Veterinaria.id_usuario == usuario.id_usuario))
    if estado:
        stmt = stmt.where(Pedido.estado_pedido == estado)
    return list(db.scalars(paginate(stmt, page)))


def change_estado_pedido(db: Session, pedido: Pedido, nuevo_estado: str, usuario: Usuario) -> Pedido:
    if nuevo_estado not in TRANSICIONES.get(pedido.estado_pedido, set()):
        raise Conflict(f"No se puede pasar de '{pedido.estado_pedido}' a '{nuevo_estado}'")
    cancela_comprador = nuevo_estado == "cancelado" and pedido.estado_pedido == "pendiente"
    if not es_veterinaria(pedido, usuario) and not cancela_comprador:
        raise Forbidden("El comprador solo puede cancelar pedidos pendientes")

    if nuevo_estado == "cancelado":
        productos = _bloquear_productos(db, [d.id_producto for d in pedido.detalles])
        for detalle in pedido.detalles:
            productos[detalle.id_producto].stock += detalle.cantidad
    if nuevo_estado == "entregado":
        pedido.fecha_entrega = datetime.now(timezone.utc)
    pedido.estado_pedido = nuevo_estado
    return save(db, pedido)
