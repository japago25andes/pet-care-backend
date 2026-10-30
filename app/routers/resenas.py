from fastapi import APIRouter, status

from app.core.deps import DB, CurrentUser, Page
from app.core.docs import errores
from app.crud import resena as resena_crud
from app.crud import veterinaria as veterinaria_crud
from app.schemas.resena import ResenaCreate, ResenaOut, ResenaUpdate

router = APIRouter(tags=["Reseñas"])


@router.get(
    "/veterinarias/{id_veterinaria}/resenas",
    response_model=list[ResenaOut],
    summary="Reseñas de una veterinaria",
    responses=errores(404),
)
def listar_resenas(id_veterinaria: int, db: DB, page: Page):
    """Público. Más recientes primero."""
    veterinaria_crud.get_veterinaria_activa(db, id_veterinaria)
    return resena_crud.list_resenas_by_veterinaria(db, id_veterinaria, page)


@router.post(
    "/veterinarias/{id_veterinaria}/resenas",
    response_model=ResenaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Reseñar veterinaria",
    responses=errores(400, 401, 403, 404, 409),
)
def crear_resena(id_veterinaria: int, resena_in: ResenaCreate, db: DB, current_user: CurrentUser):
    """
    Una reseña activa por usuario y veterinaria (409 si ya existe). No se puede reseñar la propia.
    Recalcula `calificacion_promedio` de la veterinaria.
    """
    veterinaria = veterinaria_crud.get_veterinaria_activa(db, id_veterinaria)
    return resena_crud.create_resena(db, veterinaria, current_user, resena_in)


@router.patch(
    "/resenas/{id_resena}",
    response_model=ResenaOut,
    summary="Editar mi reseña",
    responses=errores(401, 403, 404),
)
def actualizar_resena(id_resena: int, resena_in: ResenaUpdate, db: DB, current_user: CurrentUser):
    """Solo el autor. Recalcula el promedio."""
    resena = resena_crud.get_resena_activa(db, id_resena)
    return resena_crud.update_resena(db, resena, current_user, resena_in.cambios())


@router.delete(
    "/resenas/{id_resena}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar reseña",
    responses=errores(401, 403, 404),
)
def eliminar_resena(id_resena: int, db: DB, current_user: CurrentUser):
    """Autor o admin. Baja lógica; recalcula el promedio."""
    resena = resena_crud.get_resena_activa(db, id_resena)
    resena_crud.deactivate_resena(db, resena, current_user)
