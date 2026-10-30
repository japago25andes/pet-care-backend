from fastapi import APIRouter, status

from app.core.deps import DB, CurrentUser, Page
from app.core.docs import errores
from app.crud import base
from app.crud import mascota as mascota_crud
from app.crud import medicamento as medicamento_crud
from app.crud.recordatorio import validar_recordatorio_de_mascota
from app.models.medicamento import Medicamento
from app.schemas.medicamento import MedicamentoCreate, MedicamentoOut, MedicamentoUpdate

router = APIRouter(tags=["Medicamentos"], responses=errores(401))


@router.post(
    "/mascotas/{id_mascota}/medicamentos",
    response_model=MedicamentoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar medicamento",
    responses=errores(400, 404),
)
def crear_medicamento(id_mascota: int, medicamento_in: MedicamentoCreate, db: DB, current_user: CurrentUser):
    """`id_recordatorio` (opcional) debe ser un recordatorio activo de la misma mascota."""
    mascota_crud.get_mascota_accesible(db, id_mascota, current_user)
    validar_recordatorio_de_mascota(db, medicamento_in.id_recordatorio, id_mascota)
    return base.save(db, Medicamento(**medicamento_in.model_dump(), id_mascota=id_mascota))


@router.get(
    "/mascotas/{id_mascota}/medicamentos",
    response_model=list[MedicamentoOut],
    summary="Medicamentos de una mascota",
    responses=errores(404),
)
def listar_medicamentos(
    id_mascota: int, db: DB, current_user: CurrentUser, page: Page, solo_vigentes: bool = False
):
    """`solo_vigentes=true`: los que ya empezaron y no han terminado hoy."""
    mascota_crud.get_mascota_accesible(db, id_mascota, current_user)
    return medicamento_crud.list_medicamentos_by_mascota(db, id_mascota, page, solo_vigentes=solo_vigentes)


@router.get(
    "/medicamentos/{id_medicamento}",
    response_model=MedicamentoOut,
    summary="Ver medicamento",
    responses=errores(404),
)
def obtener_medicamento(id_medicamento: int, db: DB, current_user: CurrentUser):
    return medicamento_crud.get_medicamento_accesible(db, id_medicamento, current_user)


@router.patch(
    "/medicamentos/{id_medicamento}",
    response_model=MedicamentoOut,
    summary="Editar medicamento",
    responses=errores(400, 404),
)
def actualizar_medicamento(id_medicamento: int, medicamento_in: MedicamentoUpdate, db: DB, current_user: CurrentUser):
    medicamento = medicamento_crud.get_medicamento_accesible(db, id_medicamento, current_user)
    return medicamento_crud.update_medicamento(db, medicamento, medicamento_in.cambios())


@router.delete(
    "/medicamentos/{id_medicamento}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar medicamento",
    responses=errores(404),
)
def eliminar_medicamento(id_medicamento: int, db: DB, current_user: CurrentUser):
    """Baja lógica."""
    medicamento = medicamento_crud.get_medicamento_accesible(db, id_medicamento, current_user)
    base.deactivate(db, medicamento)
