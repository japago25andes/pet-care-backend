from fastapi import APIRouter, status

from app.core.deps import DB, Gestor
from app.core.docs import errores
from app.crud import base
from app.crud import profesional as profesional_crud
from app.crud import veterinaria as veterinaria_crud
from app.models.profesional import Profesional
from app.schemas.profesional import ProfesionalCreate, ProfesionalOut, ProfesionalUpdate

router = APIRouter(tags=["Profesionales"])


@router.get(
    "/veterinarias/{id_veterinaria}/profesionales",
    response_model=list[ProfesionalOut],
    summary="Profesionales de una veterinaria",
    responses=errores(404),
)
def listar_profesionales(id_veterinaria: int, db: DB):
    """Público. Solo profesionales activos de una veterinaria activa."""
    veterinaria_crud.get_veterinaria_activa(db, id_veterinaria)
    return profesional_crud.list_profesionales_by_veterinaria(db, id_veterinaria)


@router.post(
    "/veterinarias/{id_veterinaria}/profesionales",
    response_model=ProfesionalOut,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar profesional",
    responses=errores(401, 403, 404),
)
def crear_profesional(id_veterinaria: int, profesional_in: ProfesionalCreate, db: DB, current_user: Gestor):
    """Responsable de la veterinaria o admin."""
    veterinaria_crud.get_veterinaria_gestionable(db, id_veterinaria, current_user)
    return base.save(db, Profesional(**profesional_in.model_dump(), id_veterinaria=id_veterinaria))


@router.get(
    "/profesionales/{id_profesional}",
    response_model=ProfesionalOut,
    summary="Ver profesional",
    responses=errores(404),
)
def obtener_profesional(id_profesional: int, db: DB):
    """Público."""
    return profesional_crud.get_profesional_activo(db, id_profesional)


@router.patch(
    "/profesionales/{id_profesional}",
    response_model=ProfesionalOut,
    summary="Editar profesional",
    responses=errores(401, 403, 404),
)
def actualizar_profesional(id_profesional: int, profesional_in: ProfesionalUpdate, db: DB, current_user: Gestor):
    profesional = profesional_crud.get_profesional_gestionable(db, id_profesional, current_user)
    return base.update(db, profesional, profesional_in.cambios())


@router.delete(
    "/profesionales/{id_profesional}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar profesional",
    responses=errores(401, 403, 404),
)
def eliminar_profesional(id_profesional: int, db: DB, current_user: Gestor):
    """Baja lógica: ya no se le pueden agendar citas. Las existentes se conservan."""
    profesional = profesional_crud.get_profesional_gestionable(db, id_profesional, current_user)
    base.deactivate(db, profesional)
