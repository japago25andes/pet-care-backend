from fastapi import APIRouter, status

from app.core.deps import DB, CurrentUser, Page
from app.core.docs import errores
from app.crud import mensaje as mensaje_crud
from app.schemas.common import ConteoOut
from app.schemas.mensaje import MensajeCreate, MensajeOut

router = APIRouter(prefix="/mensajes", tags=["Mensajería"], responses=errores(401))


@router.post(
    "",
    response_model=MensajeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar mensaje",
    responses=errores(400, 403, 404),
)
def enviar_mensaje(mensaje_in: MensajeCreate, db: DB, current_user: CurrentUser):
    """
    Un cliente solo puede escribir a usuarios `veterinaria` o `admin`.
    Con `id_cita` debes ser parte de la cita; si no envías `id_veterinaria`, se toma de la cita.
    """
    return mensaje_crud.create_mensaje(db, current_user, mensaje_in)


@router.get("/recibidos", response_model=list[MensajeOut], summary="Bandeja de entrada")
def listar_recibidos(db: DB, current_user: CurrentUser, page: Page, solo_no_leidos: bool = False):
    return mensaje_crud.list_recibidos(db, current_user.id_usuario, page, solo_no_leidos=solo_no_leidos)


@router.get("/enviados", response_model=list[MensajeOut], summary="Mensajes enviados")
def listar_enviados(db: DB, current_user: CurrentUser, page: Page):
    return mensaje_crud.list_enviados(db, current_user.id_usuario, page)


@router.get("/no-leidos", response_model=ConteoOut, summary="Contador de no leídos")
def contar_no_leidos(db: DB, current_user: CurrentUser):
    return ConteoOut(total=mensaje_crud.count_no_leidos(db, current_user.id_usuario))


@router.get(
    "/conversacion/{id_usuario}",
    response_model=list[MensajeOut],
    summary="Conversación con un usuario",
)
def ver_conversacion(id_usuario: int, db: DB, current_user: CurrentUser, page: Page):
    """Mensajes en ambos sentidos, del más antiguo al más reciente."""
    return mensaje_crud.list_conversacion(db, current_user.id_usuario, id_usuario, page)


@router.patch(
    "/{id_mensaje}/leido",
    response_model=MensajeOut,
    summary="Marcar como leído",
    responses=errores(404),
)
def marcar_leido(id_mensaje: int, db: DB, current_user: CurrentUser):
    """Solo el destinatario."""
    return mensaje_crud.marcar_leido(db, id_mensaje, current_user)
