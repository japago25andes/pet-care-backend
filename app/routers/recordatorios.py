from fastapi import APIRouter, status

from app.core.deps import DB, CurrentUser, Page
from app.core.docs import errores
from app.crud import base
from app.crud import mascota as mascota_crud
from app.crud import recordatorio as recordatorio_crud
from app.models.recordatorio import Recordatorio
from app.schemas.common import FechaHora
from app.schemas.recordatorio import RecordatorioCreate, RecordatorioOut, RecordatorioUpdate

router = APIRouter(tags=["Recordatorios"], responses=errores(401))


@router.post(
    "/mascotas/{id_mascota}/recordatorios",
    response_model=RecordatorioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear recordatorio",
    responses=errores(404),
)
def crear_recordatorio(id_mascota: int, recordatorio_in: RecordatorioCreate, db: DB, current_user: CurrentUser):
    mascota_crud.get_mascota_accesible(db, id_mascota, current_user)
    return base.save(db, Recordatorio(**recordatorio_in.model_dump(), id_mascota=id_mascota))


@router.get(
    "/mascotas/{id_mascota}/recordatorios",
    response_model=list[RecordatorioOut],
    summary="Recordatorios de una mascota",
    responses=errores(404),
)
def listar_recordatorios_mascota(id_mascota: int, db: DB, current_user: CurrentUser, page: Page):
    """Activos, ordenados por fecha programada."""
    mascota_crud.get_mascota_accesible(db, id_mascota, current_user)
    return recordatorio_crud.list_recordatorios_by_mascota(db, id_mascota, page)


@router.get("/recordatorios", response_model=list[RecordatorioOut], summary="Todos mis recordatorios")
def listar_mis_recordatorios(
    db: DB,
    current_user: CurrentUser,
    page: Page,
    pendientes: bool = False,
    hasta: FechaHora | None = None,
):
    """
    Recordatorios activos de todas mis mascotas.
    - `pendientes=true`: ya vencidos y sin notificar (lo que hay que avisar ahora).
    - `hasta`: solo los programados hasta esa fecha.
    """
    return recordatorio_crud.list_recordatorios_by_usuario(
        db, current_user.id_usuario, page, pendientes=pendientes, hasta=hasta
    )


@router.get(
    "/recordatorios/{id_recordatorio}",
    response_model=RecordatorioOut,
    summary="Ver recordatorio",
    responses=errores(404),
)
def obtener_recordatorio(id_recordatorio: int, db: DB, current_user: CurrentUser):
    return recordatorio_crud.get_recordatorio_accesible(db, id_recordatorio, current_user)


@router.patch(
    "/recordatorios/{id_recordatorio}",
    response_model=RecordatorioOut,
    summary="Editar recordatorio",
    responses=errores(404),
)
def actualizar_recordatorio(id_recordatorio: int, recordatorio_in: RecordatorioUpdate, db: DB, current_user: CurrentUser):
    recordatorio = recordatorio_crud.get_recordatorio_accesible(db, id_recordatorio, current_user)
    cambios = recordatorio_in.cambios()
    if "fecha_programada" in cambios:
        cambios["notificado"] = False
    return base.update(db, recordatorio, cambios)


@router.post(
    "/recordatorios/{id_recordatorio}/notificado",
    response_model=RecordatorioOut,
    summary="Marcar como notificado",
    responses=errores(404),
)
def marcar_recordatorio_notificado(id_recordatorio: int, db: DB, current_user: CurrentUser):
    """
    Guarda `fecha_notificacion`. Si es único queda `notificado=true`.
    Si es recurrente (`diaria`, `semanal`, `mensual`, `anual`) avanza `fecha_programada` a la siguiente
    ocurrencia y queda pendiente otra vez.
    """
    recordatorio = recordatorio_crud.get_recordatorio_accesible(db, id_recordatorio, current_user)
    return recordatorio_crud.marcar_notificado(db, recordatorio)


@router.delete(
    "/recordatorios/{id_recordatorio}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar recordatorio",
    responses=errores(404),
)
def eliminar_recordatorio(id_recordatorio: int, db: DB, current_user: CurrentUser):
    """Baja lógica."""
    recordatorio = recordatorio_crud.get_recordatorio_accesible(db, id_recordatorio, current_user)
    base.deactivate(db, recordatorio)
