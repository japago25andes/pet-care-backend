from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.core.errors import NotFound
from app.crud.base import paginate
from app.crud.veterinaria import get_veterinaria_gestionable
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.models.veterinaria import Veterinaria


def get_producto_publico(db: Session, id_producto: int) -> Producto:
    """Producto activo de una veterinaria activa."""
    producto = db.get(Producto, id_producto)
    if producto is None or not producto.activo or not producto.veterinaria.activo:
        raise NotFound("Producto no encontrado")
    return producto


def get_producto_gestionable(db: Session, id_producto: int, usuario: Usuario) -> Producto:
    producto = db.get(Producto, id_producto)
    if producto is None:
        raise NotFound("Producto no encontrado")
    get_veterinaria_gestionable(db, producto.id_veterinaria, usuario)
    return producto


def search_productos(
    db: Session,
    page: Pagination,
    id_veterinaria: int | None = None,
    categoria: str | None = None,
    q: str | None = None,
    con_stock: bool = False,
) -> list[Producto]:
    stmt = (
        select(Producto)
        .join(Veterinaria, Producto.id_veterinaria == Veterinaria.id_veterinaria)
        .where(Producto.activo.is_(True), Veterinaria.activo.is_(True))
        .order_by(Producto.nombre_producto)
    )
    if id_veterinaria is not None:
        stmt = stmt.where(Producto.id_veterinaria == id_veterinaria)
    if categoria:
        stmt = stmt.where(Producto.categoria == categoria)
    if q:
        stmt = stmt.where(Producto.nombre_producto.icontains(q, autoescape=True))
    if con_stock:
        stmt = stmt.where(Producto.stock > 0)
    return list(db.scalars(paginate(stmt, page)))


def list_inventario(db: Session, id_veterinaria: int, page: Pagination) -> list[Producto]:
    """Todos los productos de la veterinaria, incluidos los inactivos."""
    stmt = select(Producto).where(Producto.id_veterinaria == id_veterinaria).order_by(Producto.nombre_producto)
    return list(db.scalars(paginate(stmt, page)))
