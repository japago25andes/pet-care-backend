import calendar
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.core.errors import BadRequest, NotFound
from app.core.permissions import can_access_mascota
from app.crud.base import paginate, save
from app.models.mascota import Mascota
from app.models.recordatorio import Recordatorio
from app.models.usuario import Usuario


def get_recordatorio_accesible(db: Session, id_recordatorio: int, usuario: Usuario) -> Recordatorio:
    recordatorio = db.get(Recordatorio, id_recordatorio)
    if (
        recordatorio is None
        or not recordatorio.activo
        or not recordatorio.mascota.activo
        or not can_access_mascota(usuario, recordatorio.mascota)
    ):
        raise NotFound("Recordatorio no encontrado")
    return recordatorio


def validar_recordatorio_de_mascota(db: Session, id_recordatorio: int | None, id_mascota: int) -> None:
    """Para medicamentos/vacunas: el recordatorio vinculado debe ser de la misma mascota."""
    if id_recordatorio is None:
        return
    recordatorio = db.get(Recordatorio, id_recordatorio)
    if recordatorio is None or not recordatorio.activo or recordatorio.id_mascota != id_mascota:
        raise BadRequest("El recordatorio no existe o no pertenece a esta mascota")


def list_recordatorios_by_mascota(db: Session, id_mascota: int, page: Pagination) -> list[Recordatorio]:
    stmt = (
        select(Recordatorio)
        .where(Recordatorio.id_mascota == id_mascota, Recordatorio.activo.is_(True))
        .order_by(Recordatorio.fecha_programada)
    )
    return list(db.scalars(paginate(stmt, page)))


def list_recordatorios_by_usuario(
    db: Session,
    id_usuario: int,
    page: Pagination,
    pendientes: bool = False,
    hasta: datetime | None = None,
) -> list[Recordatorio]:
    stmt = (
        select(Recordatorio)
        .join(Mascota, Recordatorio.id_mascota == Mascota.id_mascota)
        .where(Mascota.id_usuario == id_usuario, Mascota.activo.is_(True), Recordatorio.activo.is_(True))
        .order_by(Recordatorio.fecha_programada)
    )
    if pendientes:
        stmt = stmt.where(
            Recordatorio.notificado.is_(False),
            Recordatorio.fecha_programada <= datetime.now(timezone.utc),
        )
    if hasta:
        stmt = stmt.where(Recordatorio.fecha_programada <= hasta)
    return list(db.scalars(paginate(stmt, page)))


def _sumar_meses(fecha: datetime, meses: int) -> datetime:
    indice = fecha.month - 1 + meses
    anio, mes = fecha.year + indice // 12, indice % 12 + 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return fecha.replace(year=anio, month=mes, day=dia)


def _siguiente_fecha(fecha: datetime, frecuencia: str) -> datetime | None:
    match frecuencia:
        case "diaria":
            return fecha + timedelta(days=1)
        case "semanal":
            return fecha + timedelta(weeks=1)
        case "mensual":
            return _sumar_meses(fecha, 1)
        case "anual":
            return _sumar_meses(fecha, 12)
    return None


def marcar_notificado(db: Session, recordatorio: Recordatorio) -> Recordatorio:
    """Marca la notificación. Si es recurrente, pasa a la siguiente fecha y vuelve a quedar pendiente."""
    recordatorio.fecha_notificacion = datetime.now(timezone.utc)
    siguiente = _siguiente_fecha(recordatorio.fecha_programada, recordatorio.frecuencia or "unica")
    if siguiente is None:
        recordatorio.notificado = True
    else:
        recordatorio.fecha_programada = siguiente
        recordatorio.notificado = False
    return save(db, recordatorio)
