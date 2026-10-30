from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.deps import DB, Gestor, Page
from app.core.docs import errores
from app.crud import base
from app.crud import producto as producto_crud
from app.crud import veterinaria as veterinaria_crud
from app.models.producto import Producto
from app.schemas.common import CategoriaProducto
from app.schemas.producto import ProductoCreate, ProductoOut, ProductoPublicoOut, ProductoUpdate

router = APIRouter(tags=["Productos"])


@router.get("/productos", response_model=list[ProductoPublicoOut], summary="Catálogo")
def listar_productos(
    db: DB,
    page: Page,
    id_veterinaria: int | None = None,
    categoria: CategoriaProducto | None = None,
    q: Annotated[str | None, Query(description="Texto en el nombre")] = None,
    con_stock: Annotated[bool, Query(description="Solo con stock > 0")] = False,
):
    """Público. Productos activos de veterinarias activas, por nombre. No muestra `precio_compra`."""
    return producto_crud.search_productos(
        db, page, id_veterinaria=id_veterinaria, categoria=categoria, q=q, con_stock=con_stock
    )


@router.get(
    "/productos/{id_producto}",
    response_model=ProductoPublicoOut,
    summary="Ver producto",
    responses=errores(404),
)
def obtener_producto(id_producto: int, db: DB):
    """Público."""
    return producto_crud.get_producto_publico(db, id_producto)


@router.get(
    "/veterinarias/{id_veterinaria}/inventario",
    response_model=list[ProductoOut],
    summary="Inventario de mi veterinaria",
    responses=errores(401, 403, 404),
)
def listar_inventario(id_veterinaria: int, db: DB, current_user: Gestor, page: Page):
    """Responsable o admin. Incluye inactivos y `precio_compra`."""
    veterinaria_crud.get_veterinaria_gestionable(db, id_veterinaria, current_user)
    return producto_crud.list_inventario(db, id_veterinaria, page)


@router.post(
    "/veterinarias/{id_veterinaria}/productos",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    responses=errores(401, 403, 404),
)
def crear_producto(id_veterinaria: int, producto_in: ProductoCreate, db: DB, current_user: Gestor):
    """Responsable de la veterinaria o admin."""
    veterinaria_crud.get_veterinaria_gestionable(db, id_veterinaria, current_user)
    return base.save(db, Producto(**producto_in.model_dump(), id_veterinaria=id_veterinaria))


@router.patch(
    "/productos/{id_producto}",
    response_model=ProductoOut,
    summary="Editar producto / ajustar stock",
    responses=errores(401, 403, 404),
)
def actualizar_producto(id_producto: int, producto_in: ProductoUpdate, db: DB, current_user: Gestor):
    """El nuevo precio de venta se refleja en los carritos activos la próxima vez que se consulten."""
    producto = producto_crud.get_producto_gestionable(db, id_producto, current_user)
    return base.update(db, producto, producto_in.cambios())


@router.delete(
    "/productos/{id_producto}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar producto",
    responses=errores(401, 403, 404),
)
def eliminar_producto(id_producto: int, db: DB, current_user: Gestor):
    """Baja lógica: sale del catálogo y no se puede comprar."""
    producto = producto_crud.get_producto_gestionable(db, id_producto, current_user)
    base.deactivate(db, producto)
