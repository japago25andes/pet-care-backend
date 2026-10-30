from fastapi import APIRouter, status

from app.core.deps import DB, CurrentUser
from app.core.docs import errores
from app.core.errors import Conflict
from app.crud import base
from app.crud import mascota as mascota_crud
from app.models.mascota import Mascota
from app.schemas.mascota import MascotaCreate, MascotaOut, MascotaUpdate

router = APIRouter(prefix="/mascotas", tags=["Mascotas"], responses=errores(401))

CHIP_DUPLICADO = "Ya existe una mascota activa con ese número de chip"


@router.post(
    "",
    response_model=MascotaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar mascota",
    responses=errores(409),
)
def crear_mascota(mascota_in: MascotaCreate, db: DB, current_user: CurrentUser):
    """La mascota queda a nombre del usuario autenticado."""
    if mascota_in.numero_chip and mascota_crud.chip_en_uso(db, mascota_in.numero_chip):
        raise Conflict(CHIP_DUPLICADO)
    return base.save(db, Mascota(**mascota_in.model_dump(), id_usuario=current_user.id_usuario))


@router.get("", response_model=list[MascotaOut], summary="Mis mascotas")
def listar_mascotas(db: DB, current_user: CurrentUser):
    """Mascotas activas del usuario autenticado."""
    return mascota_crud.list_mascotas_by_usuario(db, id_usuario=current_user.id_usuario)


@router.get("/{id_mascota}", response_model=MascotaOut, summary="Ver mascota", responses=errores(404))
def obtener_mascota(id_mascota: int, db: DB, current_user: CurrentUser):
    return mascota_crud.get_mascota_accesible(db, id_mascota, current_user)


@router.patch(
    "/{id_mascota}",
    response_model=MascotaOut,
    summary="Editar mascota",
    responses=errores(404, 409),
)
def actualizar_mascota(id_mascota: int, mascota_in: MascotaUpdate, db: DB, current_user: CurrentUser):
    """Solo cambia los campos enviados. `nombre` y `especie` no aceptan null."""
    mascota = mascota_crud.get_mascota_accesible(db, id_mascota, current_user)
    cambios = mascota_in.cambios()
    nuevo_chip = cambios.get("numero_chip")
    if nuevo_chip and mascota_crud.chip_en_uso(db, nuevo_chip, excluir_id=mascota.id_mascota):
        raise Conflict(CHIP_DUPLICADO)
    return base.update(db, mascota, cambios)


@router.delete(
    "/{id_mascota}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar mascota",
    responses=errores(404),
)
def eliminar_mascota(id_mascota: int, db: DB, current_user: CurrentUser):
    """Baja lógica: libera el chip, cancela sus citas futuras y desactiva sus recordatorios."""
    mascota = mascota_crud.get_mascota_accesible(db, id_mascota, current_user)
    mascota_crud.deactivate_mascota(db, mascota)
