import math

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.core.errors import Forbidden, NotFound
from app.core.permissions import can_manage_veterinaria
from app.crud.base import paginate
from app.models.usuario import Usuario
from app.models.veterinaria import Veterinaria

RADIO_TIERRA_KM = 6371


def get_veterinaria_activa(db: Session, id_veterinaria: int) -> Veterinaria:
    veterinaria = db.get(Veterinaria, id_veterinaria)
    if veterinaria is None or not veterinaria.activo:
        raise NotFound("Veterinaria no encontrada")
    return veterinaria


def get_veterinaria_gestionable(db: Session, id_veterinaria: int, usuario: Usuario) -> Veterinaria:
    """Veterinaria que el usuario puede administrar (su responsable o un admin)."""
    veterinaria = db.get(Veterinaria, id_veterinaria)
    if veterinaria is None:
        raise NotFound("Veterinaria no encontrada")
    if not can_manage_veterinaria(usuario, veterinaria):
        raise Forbidden("Solo el responsable de la veterinaria o un admin puede hacer esto")
    return veterinaria


def _distancia_km(lat: float, lng: float):
    """Fórmula de Haversine (ley de cosenos) en SQL."""
    lat_r, lng_r = math.radians(lat), math.radians(lng)
    coseno = math.cos(lat_r) * func.cos(func.radians(Veterinaria.latitud)) * func.cos(
        func.radians(Veterinaria.longitud) - lng_r
    ) + math.sin(lat_r) * func.sin(func.radians(Veterinaria.latitud))
    return RADIO_TIERRA_KM * func.acos(func.least(1.0, func.greatest(-1.0, coseno)))


def search_veterinarias(
    db: Session,
    page: Pagination,
    q: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radio_km: float = 10,
) -> list[Veterinaria]:
    stmt = select(Veterinaria).where(Veterinaria.activo.is_(True))
    if q:
        stmt = stmt.where(Veterinaria.nombre_comercial.icontains(q, autoescape=True))

    if lat is None or lng is None:
        stmt = stmt.order_by(Veterinaria.calificacion_promedio.desc(), Veterinaria.nombre_comercial)
        return list(db.scalars(paginate(stmt, page)))

    distancia = _distancia_km(lat, lng)
    stmt = (
        stmt.add_columns(distancia)
        .where(Veterinaria.latitud.is_not(None), Veterinaria.longitud.is_not(None), distancia <= radio_km)
        .order_by(distancia)
    )
    resultado = []
    for veterinaria, km in db.execute(paginate(stmt, page)):
        veterinaria.distancia_km = round(km, 2)
        resultado.append(veterinaria)
    return resultado


def list_veterinarias_by_usuario(db: Session, id_usuario: int) -> list[Veterinaria]:
    stmt = select(Veterinaria).where(Veterinaria.id_usuario == id_usuario).order_by(Veterinaria.id_veterinaria)
    return list(db.scalars(stmt))
