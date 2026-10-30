from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFound
from app.crud.veterinaria import get_veterinaria_gestionable
from app.models.profesional import Profesional
from app.models.usuario import Usuario


def get_profesional_activo(db: Session, id_profesional: int) -> Profesional:
    """Profesional activo de una veterinaria activa."""
    profesional = db.get(Profesional, id_profesional)
    if profesional is None or not profesional.activo or not profesional.veterinaria.activo:
        raise NotFound("Profesional no encontrado")
    return profesional


def get_profesional_gestionable(db: Session, id_profesional: int, usuario: Usuario) -> Profesional:
    profesional = db.get(Profesional, id_profesional)
    if profesional is None:
        raise NotFound("Profesional no encontrado")
    get_veterinaria_gestionable(db, profesional.id_veterinaria, usuario)
    return profesional


def list_profesionales_by_veterinaria(db: Session, id_veterinaria: int) -> list[Profesional]:
    stmt = (
        select(Profesional)
        .where(Profesional.id_veterinaria == id_veterinaria, Profesional.activo.is_(True))
        .order_by(Profesional.nombre_completo)
    )
    return list(db.scalars(stmt))
