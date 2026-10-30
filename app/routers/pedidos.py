from fastapi import APIRouter, status

from app.core.deps import DB, CurrentUser, Page
from app.core.docs import errores
from app.crud import pedido as pedido_crud
from app.schemas.common import EstadoPedido
from app.schemas.pedido import PedidoCreate, PedidoEstadoUpdate, PedidoOut

router = APIRouter(prefix="/pedidos", tags=["Pedidos"], responses=errores(401))


@router.post(
    "",
    response_model=PedidoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Confirmar compra (checkout)",
    responses=errores(400, 409),
)
def crear_pedido(pedido_in: PedidoCreate, db: DB, current_user: CurrentUser):
    """
    Convierte el carrito activo en un pedido `pendiente`:
    valida disponibilidad y stock, descuenta stock, fija precios y total, y cierra el carrito.
    No procesa pagos: `metodo_pago` es informativo.
    """
    return pedido_crud.create_pedido(db, current_user, pedido_in)


@router.get("", response_model=list[PedidoOut], summary="Mis pedidos")
def listar_pedidos(db: DB, current_user: CurrentUser, page: Page, estado: EstadoPedido | None = None):
    """Mis compras + pedidos recibidos por las veterinarias que gestiono (admin: todos). Más recientes primero."""
    return pedido_crud.list_pedidos(db, current_user, page, estado=estado)


@router.get("/{id_pedido}", response_model=PedidoOut, summary="Ver pedido", responses=errores(404))
def obtener_pedido(id_pedido: int, db: DB, current_user: CurrentUser):
    return pedido_crud.get_pedido_accesible(db, id_pedido, current_user)


@router.patch(
    "/{id_pedido}/estado",
    response_model=PedidoOut,
    summary="Cambiar estado del pedido",
    responses=errores(403, 404, 409),
)
def cambiar_estado_pedido(id_pedido: int, datos: PedidoEstadoUpdate, db: DB, current_user: CurrentUser):
    """
    Transiciones válidas:
    - `pendiente` → `confirmado` | `cancelado`
    - `confirmado` → `enviado` | `cancelado`
    - `enviado` → `entregado` (guarda `fecha_entrega`)

    El comprador solo puede cancelar si está `pendiente`; el resto lo hace la veterinaria.
    Cancelar devuelve el stock.
    """
    pedido = pedido_crud.get_pedido_accesible(db, id_pedido, current_user)
    return pedido_crud.change_estado_pedido(db, pedido, datos.estado, current_user)
