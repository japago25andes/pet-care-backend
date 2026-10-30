from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.deps import DB, Gestor, Page
from app.core.docs import errores
from app.core.errors import BadRequest, Forbidden
from app.core.permissions import is_admin
from app.crud import base
from app.crud import veterinaria as veterinaria_crud
from app.models.veterinaria import Veterinaria
from app.schemas.veterinaria import VeterinariaCreate, VeterinariaOut, VeterinariaUpdate

router = APIRouter(prefix="/veterinarias", tags=["Veterinarias"])


@router.get("", response_model=list[VeterinariaOut], summary="Buscar veterinarias", responses=errores(400))
def listar_veterinarias(
    db: DB,
    page: Page,
    q: Annotated[str | None, Query(description="Texto en el nombre comercial")] = None,
    lat: Annotated[float | None, Query(ge=-90, le=90, description="Tu latitud")] = None,
    lng: Annotated[float | None, Query(ge=-180, le=180, description="Tu longitud")] = None,
    radio_km: Annotated[float, Query(gt=0, le=500, description="Radio de búsqueda con lat/lng")] = 10,
):
    """
    Público. Solo veterinarias activas.
    - Sin `lat`/`lng`: ordenadas por calificación.
    - Con `lat` y `lng`: solo las que están dentro de `radio_km`, de la más cercana a la más lejana, con `distancia_km`.
    """
    if (lat is None) != (lng is None):
        raise BadRequest("Envía lat y lng juntos")
    return veterinaria_crud.search_veterinarias(db, page, q=q, lat=lat, lng=lng, radio_km=radio_km)


@router.get(
    "/mias",
    response_model=list[VeterinariaOut],
    summary="Mis veterinarias",
    responses=errores(401, 403),
)
def listar_mis_veterinarias(db: DB, current_user: Gestor):
    """Veterinarias de las que soy responsable, incluidas las inactivas."""
    return veterinaria_crud.list_veterinarias_by_usuario(db, current_user.id_usuario)


@router.post(
    "",
    response_model=VeterinariaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar veterinaria",
    responses=errores(401, 403),
)
def crear_veterinaria(veterinaria_in: VeterinariaCreate, db: DB, current_user: Gestor):
    """Rol `veterinaria` o `admin`. El usuario autenticado queda como responsable."""
    return base.save(db, Veterinaria(**veterinaria_in.model_dump(), id_usuario=current_user.id_usuario))


@router.get("/{id_veterinaria}", response_model=VeterinariaOut, summary="Ver veterinaria", responses=errores(404))
def obtener_veterinaria(id_veterinaria: int, db: DB):
    """Público. 404 si está inactiva."""
    return veterinaria_crud.get_veterinaria_activa(db, id_veterinaria)


@router.patch(
    "/{id_veterinaria}",
    response_model=VeterinariaOut,
    summary="Editar veterinaria",
    responses=errores(401, 403, 404),
)
def actualizar_veterinaria(id_veterinaria: int, veterinaria_in: VeterinariaUpdate, db: DB, current_user: Gestor):
    """Responsable o admin. Solo un admin puede cambiar `activo`."""
    veterinaria = veterinaria_crud.get_veterinaria_gestionable(db, id_veterinaria, current_user)
    cambios = veterinaria_in.cambios()
    if "activo" in cambios and not is_admin(current_user):
        raise Forbidden("Solo un admin puede cambiar el estado de la veterinaria")
    return base.update(db, veterinaria, cambios)


@router.delete(
    "/{id_veterinaria}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar veterinaria",
    responses=errores(401, 403, 404),
)
def eliminar_veterinaria(id_veterinaria: int, db: DB, current_user: Gestor):
    """Baja lógica: deja de aparecer en búsquedas, tienda y no acepta citas nuevas."""
    veterinaria = veterinaria_crud.get_veterinaria_gestionable(db, id_veterinaria, current_user)
    base.deactivate(db, veterinaria)
