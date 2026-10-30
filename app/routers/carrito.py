from fastapi import APIRouter

from app.core.deps import DB, CurrentUser
from app.core.docs import errores
from app.crud import carrito as carrito_crud
from app.schemas.carrito import CarritoOut, ItemCarritoCreate, ItemCarritoUpdate

router = APIRouter(prefix="/carrito", tags=["Carrito"], responses=errores(401))


@router.get("", response_model=CarritoOut, summary="Ver mi carrito")
def obtener_carrito(db: DB, current_user: CurrentUser):
    """Crea el carrito si no existe. Los precios se actualizan al precio de venta vigente."""
    carrito = carrito_crud.get_or_create_carrito(db, current_user)
    return carrito_crud.sync_precios(db, carrito)


@router.post("/items", response_model=CarritoOut, summary="Agregar producto", responses=errores(404, 409))
def agregar_item(item_in: ItemCarritoCreate, db: DB, current_user: CurrentUser):
    """
    Si el producto ya está, suma la cantidad.
    409 si supera el stock o si es de otra veterinaria (un carrito = una veterinaria).
    """
    carrito = carrito_crud.get_or_create_carrito(db, current_user)
    return carrito_crud.add_item(db, carrito, item_in.id_producto, item_in.cantidad)


@router.patch(
    "/items/{id_detalle_carrito}",
    response_model=CarritoOut,
    summary="Cambiar cantidad",
    responses=errores(404, 409),
)
def actualizar_item(id_detalle_carrito: int, item_in: ItemCarritoUpdate, db: DB, current_user: CurrentUser):
    carrito = carrito_crud.get_or_create_carrito(db, current_user)
    return carrito_crud.update_item(db, carrito, id_detalle_carrito, item_in.cantidad)


@router.delete(
    "/items/{id_detalle_carrito}",
    response_model=CarritoOut,
    summary="Quitar producto",
    responses=errores(404),
)
def quitar_item(id_detalle_carrito: int, db: DB, current_user: CurrentUser):
    carrito = carrito_crud.get_or_create_carrito(db, current_user)
    return carrito_crud.remove_item(db, carrito, id_detalle_carrito)


@router.delete("", response_model=CarritoOut, summary="Vaciar carrito")
def vaciar_carrito(db: DB, current_user: CurrentUser):
    carrito = carrito_crud.get_or_create_carrito(db, current_user)
    return carrito_crud.vaciar(db, carrito)
