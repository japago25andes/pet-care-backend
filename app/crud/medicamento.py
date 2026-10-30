from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.core.errors import BadRequest, NotFound
from app.core.permissions import can_access_mascota
from app.crud.base import paginate, update
from app.crud.recordatorio import validar_recordatorio_de_mascota
from app.models.medicamento import Medicamento
from app.models.usuario import Usuario


def get_medicamento_accesible(db: Session, id_medicamento: int, usuario: Usuario) -> Medicamento:
    medicamento = db.get(Medicamento, id_medicamento)
    if (
        medicamento is None
        or not medicamento.activo
        or not medicamento.mascota.activo
        or not can_access_mascota(usuario, medicamento.mascota)
    ):
        raise NotFound("Medicamento no encontrado")
    return medicamento


def list_medicamentos_by_mascota(
    db: Session, id_mascota: int, page: Pagination, solo_vigentes: bool = False
) -> list[Medicamento]:
    stmt = (
        select(Medicamento)
        .where(Medicamento.id_mascota == id_mascota, Medicamento.activo.is_(True))
        .order_by(Medicamento.fecha_inicio.desc())
    )
    if solo_vigentes:
        hoy = date.today()
        stmt = stmt.where(
            Medicamento.fecha_inicio <= hoy,
            or_(Medicamento.fecha_fin.is_(None), Medicamento.fecha_fin >= hoy),
        )
    return list(db.scalars(paginate(stmt, page)))


def update_medicamento(db: Session, medicamento: Medicamento, cambios: dict) -> Medicamento:
    if "id_recordatorio" in cambios:
        validar_recordatorio_de_mascota(db, cambios["id_recordatorio"], medicamento.id_mascota)
    inicio = cambios.get("fecha_inicio", medicamento.fecha_inicio)
    fin = cambios.get("fecha_fin", medicamento.fecha_fin)
    if fin is not None and fin < inicio:
        raise BadRequest("fecha_fin no puede ser anterior a fecha_inicio")
    return update(db, medicamento, cambios)
