from fastapi import APIRouter, status

from app.core.deps import DB, CurrentUser, Page
from app.core.docs import errores
from app.crud import base
from app.crud import mascota as mascota_crud
from app.crud import vacuna as vacuna_crud
from app.crud.recordatorio import validar_recordatorio_de_mascota
from app.models.vacuna import Vacuna
from app.schemas.vacuna import VacunaCreate, VacunaOut, VacunaUpdate

router = APIRouter(tags=["Vacunas"], responses=errores(401))


@router.post(
    "/mascotas/{id_mascota}/vacunas",
    response_model=VacunaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar vacuna aplicada",
    responses=errores(400, 404),
)
def crear_vacuna(id_mascota: int, vacuna_in: VacunaCreate, db: DB, current_user: CurrentUser):
    """`id_recordatorio` (opcional) debe ser un recordatorio activo de la misma mascota."""
    mascota_crud.get_mascota_accesible(db, id_mascota, current_user)
    validar_recordatorio_de_mascota(db, vacuna_in.id_recordatorio, id_mascota)
    return base.save(db, Vacuna(**vacuna_in.model_dump(), id_mascota=id_mascota))


@router.get(
    "/mascotas/{id_mascota}/vacunas",
    response_model=list[VacunaOut],
    summary="Carné de vacunas",
    responses=errores(404),
)
def listar_vacunas(id_mascota: int, db: DB, current_user: CurrentUser, page: Page):
    """De la más reciente a la más antigua."""
    mascota_crud.get_mascota_accesible(db, id_mascota, current_user)
    return vacuna_crud.list_vacunas_by_mascota(db, id_mascota, page)


@router.get("/vacunas/{id_vacuna}", response_model=VacunaOut, summary="Ver vacuna", responses=errores(404))
def obtener_vacuna(id_vacuna: int, db: DB, current_user: CurrentUser):
    return vacuna_crud.get_vacuna_accesible(db, id_vacuna, current_user)


@router.patch(
    "/vacunas/{id_vacuna}",
    response_model=VacunaOut,
    summary="Editar vacuna",
    responses=errores(400, 404),
)
def actualizar_vacuna(id_vacuna: int, vacuna_in: VacunaUpdate, db: DB, current_user: CurrentUser):
    vacuna = vacuna_crud.get_vacuna_accesible(db, id_vacuna, current_user)
    return vacuna_crud.update_vacuna(db, vacuna, vacuna_in.cambios())


@router.delete(
    "/vacunas/{id_vacuna}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar vacuna",
    responses=errores(404),
)
def eliminar_vacuna(id_vacuna: int, db: DB, current_user: CurrentUser):
    """Borrado definitivo (la tabla no tiene `activo`)."""
    vacuna = vacuna_crud.get_vacuna_accesible(db, id_vacuna, current_user)
    db.delete(vacuna)
    db.commit()
