from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.core.errors import BadRequest, Conflict, Forbidden, NotFound
from app.core.permissions import is_admin
from app.crud.base import paginate, save, update
from app.crud.mascota import get_mascota_accesible
from app.crud.profesional import get_profesional_activo
from app.models.cita import CitaVeterinaria
from app.models.mascota import Mascota
from app.models.usuario import Usuario
from app.models.veterinaria import Veterinaria
from app.schemas.cita import CitaCreate

ESTADOS_ACTIVOS = ("programada", "confirmada")
TRANSICIONES = {
    "programada": {"confirmada", "cancelada"},
    "confirmada": {"completada", "cancelada", "no_asistio"},
}


def es_duenio(cita: CitaVeterinaria, usuario: Usuario) -> bool:
    return cita.mascota.id_usuario == usuario.id_usuario


def es_veterinaria(cita: CitaVeterinaria, usuario: Usuario) -> bool:
    return is_admin(usuario) or cita.veterinaria.id_usuario == usuario.id_usuario


def get_cita_accesible(db: Session, id_cita: int, usuario: Usuario) -> CitaVeterinaria:
    """Cita donde el usuario es dueño de la mascota o responsable de la veterinaria."""
    cita = db.get(CitaVeterinaria, id_cita)
    if cita is None or not (es_duenio(cita, usuario) or es_veterinaria(cita, usuario)):
        raise NotFound("Cita no encontrada")
    return cita


def _validar_horario(db: Session, id_profesional: int, fecha_cita: datetime, excluir_id: int | None = None) -> None:
    if fecha_cita <= datetime.now(timezone.utc):
        raise BadRequest("La cita debe ser en una fecha futura")
    stmt = select(CitaVeterinaria.id_cita).where(
        CitaVeterinaria.id_profesional == id_profesional,
        CitaVeterinaria.fecha_cita == fecha_cita,
        CitaVeterinaria.estado.in_(ESTADOS_ACTIVOS),
    )
    if excluir_id is not None:
        stmt = stmt.where(CitaVeterinaria.id_cita != excluir_id)
    if db.scalar(stmt) is not None:
        raise Conflict("El profesional ya tiene una cita en ese horario")


def create_cita(db: Session, cita_in: CitaCreate, usuario: Usuario) -> CitaVeterinaria:
    get_mascota_accesible(db, cita_in.id_mascota, usuario)
    profesional = get_profesional_activo(db, cita_in.id_profesional)
    _validar_horario(db, profesional.id_profesional, cita_in.fecha_cita)
    cita = CitaVeterinaria(
        **cita_in.model_dump(),
        id_veterinaria=profesional.id_veterinaria,
        estado="programada",
    )
    return save(db, cita)


def list_citas(
    db: Session,
    usuario: Usuario,
    page: Pagination,
    estado: str | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
) -> list[CitaVeterinaria]:
    stmt = (
        select(CitaVeterinaria)
        .join(Mascota, CitaVeterinaria.id_mascota == Mascota.id_mascota)
        .join(Veterinaria, CitaVeterinaria.id_veterinaria == Veterinaria.id_veterinaria)
        .order_by(CitaVeterinaria.fecha_cita)
    )
    if not is_admin(usuario):
        stmt = stmt.where(or_(Mascota.id_usuario == usuario.id_usuario, Veterinaria.id_usuario == usuario.id_usuario))
    if estado:
        stmt = stmt.where(CitaVeterinaria.estado == estado)
    if desde:
        stmt = stmt.where(CitaVeterinaria.fecha_cita >= desde)
    if hasta:
        stmt = stmt.where(CitaVeterinaria.fecha_cita <= hasta)
    return list(db.scalars(paginate(stmt, page)))


def update_cita(db: Session, cita: CitaVeterinaria, cambios: dict, usuario: Usuario) -> CitaVeterinaria:
    if cita.estado not in ESTADOS_ACTIVOS:
        raise Conflict("Solo se pueden modificar citas programadas o confirmadas")
    if "notas" in cambios and not es_veterinaria(cita, usuario):
        raise Forbidden("Solo la veterinaria puede escribir notas")
    nueva_fecha = cambios.get("fecha_cita")
    if nueva_fecha is not None and nueva_fecha != cita.fecha_cita:
        _validar_horario(db, cita.id_profesional, nueva_fecha, excluir_id=cita.id_cita)
        cambios["estado"] = "programada"
    return update(db, cita, cambios)


def change_estado_cita(db: Session, cita: CitaVeterinaria, nuevo_estado: str, usuario: Usuario) -> CitaVeterinaria:
    if nuevo_estado not in TRANSICIONES.get(cita.estado, set()):
        raise Conflict(f"No se puede pasar de '{cita.estado}' a '{nuevo_estado}'")
    if nuevo_estado != "cancelada" and not es_veterinaria(cita, usuario):
        raise Forbidden("El dueño de la mascota solo puede cancelar la cita")
    cita.estado = nuevo_estado
    return save(db, cita)
