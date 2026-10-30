from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.errors import NotFound
from app.core.permissions import can_access_mascota
from app.models.cita import CitaVeterinaria
from app.models.mascota import Mascota
from app.models.recordatorio import Recordatorio
from app.models.usuario import Usuario


def get_mascota_accesible(db: Session, id_mascota: int, usuario: Usuario) -> Mascota:
    """Mascota activa del usuario (o cualquiera si es admin). Si no, 404."""
    mascota = db.get(Mascota, id_mascota)
    if mascota is None or not mascota.activo or not can_access_mascota(usuario, mascota):
        raise NotFound("Mascota no encontrada")
    return mascota


def chip_en_uso(db: Session, numero_chip: str, excluir_id: int | None = None) -> bool:
    stmt = select(Mascota.id_mascota).where(Mascota.numero_chip == numero_chip, Mascota.activo.is_(True))
    if excluir_id is not None:
        stmt = stmt.where(Mascota.id_mascota != excluir_id)
    return db.scalar(stmt) is not None


def list_mascotas_by_usuario(db: Session, id_usuario: int) -> list[Mascota]:
    stmt = (
        select(Mascota)
        .where(Mascota.id_usuario == id_usuario, Mascota.activo.is_(True))
        .order_by(Mascota.id_mascota)
    )
    return list(db.scalars(stmt))


def deactivate_mascota(db: Session, mascota: Mascota) -> None:
    """Desactiva la mascota, cancela sus citas futuras y desactiva sus recordatorios."""
    mascota.activo = False
    db.execute(
        update(CitaVeterinaria)
        .where(
            CitaVeterinaria.id_mascota == mascota.id_mascota,
            CitaVeterinaria.estado.in_(("programada", "confirmada")),
            CitaVeterinaria.fecha_cita > datetime.now(timezone.utc),
        )
        .values(estado="cancelada")
    )
    db.execute(update(Recordatorio).where(Recordatorio.id_mascota == mascota.id_mascota).values(activo=False))
    db.commit()
