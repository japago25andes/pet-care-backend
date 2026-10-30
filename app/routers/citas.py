from fastapi import APIRouter, status

from app.core.deps import DB, CurrentUser, Page
from app.core.docs import errores
from app.crud import cita as cita_crud
from app.schemas.cita import CitaCreate, CitaEstadoUpdate, CitaOut, CitaUpdate
from app.schemas.common import EstadoCita, FechaHora

router = APIRouter(prefix="/citas", tags=["Citas"], responses=errores(401))


@router.post(
    "",
    response_model=CitaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Agendar cita",
    responses=errores(400, 404, 409),
)
def crear_cita(cita_in: CitaCreate, db: DB, current_user: CurrentUser):
    """
    Para una mascota propia y un profesional activo. Queda en estado `programada`.
    409 si el profesional ya tiene otra cita activa a esa misma hora.
    """
    return cita_crud.create_cita(db, cita_in, current_user)


@router.get("", response_model=list[CitaOut], summary="Mis citas")
def listar_citas(
    db: DB,
    current_user: CurrentUser,
    page: Page,
    estado: EstadoCita | None = None,
    desde: FechaHora | None = None,
    hasta: FechaHora | None = None,
):
    """Citas de mis mascotas + citas de las veterinarias que gestiono (admin: todas). Orden por fecha."""
    return cita_crud.list_citas(db, current_user, page, estado=estado, desde=desde, hasta=hasta)


@router.get("/{id_cita}", response_model=CitaOut, summary="Ver cita", responses=errores(404))
def obtener_cita(id_cita: int, db: DB, current_user: CurrentUser):
    return cita_crud.get_cita_accesible(db, id_cita, current_user)


@router.patch(
    "/{id_cita}",
    response_model=CitaOut,
    summary="Reprogramar o editar cita",
    responses=errores(400, 403, 404, 409),
)
def actualizar_cita(id_cita: int, cita_in: CitaUpdate, db: DB, current_user: CurrentUser):
    """
    Solo citas `programada` o `confirmada`. Cambiar `fecha_cita` la devuelve a `programada`.
    `notas` solo las escribe la veterinaria.
    """
    cita = cita_crud.get_cita_accesible(db, id_cita, current_user)
    return cita_crud.update_cita(db, cita, cita_in.cambios(), current_user)


@router.patch(
    "/{id_cita}/estado",
    response_model=CitaOut,
    summary="Cambiar estado de la cita",
    responses=errores(403, 404, 409),
)
def cambiar_estado_cita(id_cita: int, datos: CitaEstadoUpdate, db: DB, current_user: CurrentUser):
    """
    Transiciones válidas:
    - `programada` → `confirmada` | `cancelada`
    - `confirmada` → `completada` | `cancelada` | `no_asistio`

    El dueño de la mascota solo puede **cancelar**; el resto lo hace la veterinaria.
    """
    cita = cita_crud.get_cita_accesible(db, id_cita, current_user)
    return cita_crud.change_estado_cita(db, cita, datos.estado, current_user)
