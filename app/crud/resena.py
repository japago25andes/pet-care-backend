from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.core.errors import BadRequest, Conflict, Forbidden, NotFound
from app.core.permissions import is_admin
from app.crud.base import paginate
from app.models.pedido import Pedido
from app.models.resena import Resena
from app.models.usuario import Usuario
from app.models.veterinaria import Veterinaria
from app.schemas.resena import ResenaCreate


def _recalcular_promedio(db: Session, id_veterinaria: int) -> None:
    db.flush()
    promedio = db.scalar(
        select(func.avg(Resena.calificacion)).where(
            Resena.id_veterinaria == id_veterinaria, Resena.activo.is_(True)
        )
    )
    veterinaria = db.get(Veterinaria, id_veterinaria)
    veterinaria.calificacion_promedio = round(Decimal(promedio or 0), 2)


def _guardar(db: Session, resena: Resena) -> Resena:
    _recalcular_promedio(db, resena.id_veterinaria)
    db.commit()
    db.refresh(resena)
    return resena


def get_resena_activa(db: Session, id_resena: int) -> Resena:
    resena = db.get(Resena, id_resena)
    if resena is None or not resena.activo:
        raise NotFound("Reseña no encontrada")
    return resena


def create_resena(db: Session, veterinaria: Veterinaria, usuario: Usuario, resena_in: ResenaCreate) -> Resena:
    if veterinaria.id_usuario == usuario.id_usuario:
        raise Forbidden("No puedes reseñar tu propia veterinaria")
    existente = db.scalar(
        select(Resena.id_resena).where(
            Resena.id_usuario == usuario.id_usuario,
            Resena.id_veterinaria == veterinaria.id_veterinaria,
            Resena.activo.is_(True),
        )
    )
    if existente is not None:
        raise Conflict("Ya reseñaste esta veterinaria; edita tu reseña existente")
    if resena_in.id_pedido is not None:
        pedido = db.get(Pedido, resena_in.id_pedido)
        if (
            pedido is None
            or pedido.id_usuario != usuario.id_usuario
            or pedido.id_veterinaria != veterinaria.id_veterinaria
            or pedido.estado_pedido != "entregado"
        ):
            raise BadRequest("El pedido debe ser tuyo, de esta veterinaria y estar entregado")

    resena = Resena(**resena_in.model_dump(), id_usuario=usuario.id_usuario, id_veterinaria=veterinaria.id_veterinaria)
    db.add(resena)
    return _guardar(db, resena)


def list_resenas_by_veterinaria(db: Session, id_veterinaria: int, page: Pagination) -> list[Resena]:
    stmt = (
        select(Resena)
        .where(Resena.id_veterinaria == id_veterinaria, Resena.activo.is_(True))
        .order_by(Resena.fecha_creacion.desc())
    )
    return list(db.scalars(paginate(stmt, page)))


def update_resena(db: Session, resena: Resena, usuario: Usuario, cambios: dict) -> Resena:
    if resena.id_usuario != usuario.id_usuario:
        raise Forbidden("Solo el autor puede editar la reseña")
    for campo, valor in cambios.items():
        setattr(resena, campo, valor)
    return _guardar(db, resena)


def deactivate_resena(db: Session, resena: Resena, usuario: Usuario) -> None:
    if resena.id_usuario != usuario.id_usuario and not is_admin(usuario):
        raise Forbidden("Solo el autor o un admin puede eliminar la reseña")
    resena.activo = False
    _guardar(db, resena)
