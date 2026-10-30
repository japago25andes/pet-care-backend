from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.core.errors import BadRequest, NotFound
from app.core.permissions import can_access_mascota
from app.crud.base import paginate, update
from app.crud.recordatorio import validar_recordatorio_de_mascota
from app.models.usuario import Usuario
from app.models.vacuna import Vacuna


def get_vacuna_accesible(db: Session, id_vacuna: int, usuario: Usuario) -> Vacuna:
    vacuna = db.get(Vacuna, id_vacuna)
    if vacuna is None or not vacuna.mascota.activo or not can_access_mascota(usuario, vacuna.mascota):
        raise NotFound("Vacuna no encontrada")
    return vacuna


def list_vacunas_by_mascota(db: Session, id_mascota: int, page: Pagination) -> list[Vacuna]:
    stmt = select(Vacuna).where(Vacuna.id_mascota == id_mascota).order_by(Vacuna.fecha_aplicacion.desc())
    return list(db.scalars(paginate(stmt, page)))


def update_vacuna(db: Session, vacuna: Vacuna, cambios: dict) -> Vacuna:
    if "id_recordatorio" in cambios:
        validar_recordatorio_de_mascota(db, cambios["id_recordatorio"], vacuna.id_mascota)
    aplicacion = cambios.get("fecha_aplicacion", vacuna.fecha_aplicacion)
    proxima = cambios.get("fecha_proxima_dosis", vacuna.fecha_proxima_dosis)
    if aplicacion > date.today():
        raise BadRequest("fecha_aplicacion no puede ser futura")
    if proxima is not None and proxima <= aplicacion:
        raise BadRequest("fecha_proxima_dosis debe ser posterior a fecha_aplicacion")
    return update(db, vacuna, cambios)
