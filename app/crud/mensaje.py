from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.core.errors import BadRequest, Forbidden, NotFound
from app.crud.base import paginate, save
from app.crud.cita import es_duenio, es_veterinaria
from app.crud.veterinaria import get_veterinaria_activa
from app.models.cita import CitaVeterinaria
from app.models.mensaje import Mensaje
from app.models.usuario import Usuario
from app.schemas.mensaje import MensajeCreate


def create_mensaje(db: Session, remitente: Usuario, mensaje_in: MensajeCreate) -> Mensaje:
    if mensaje_in.id_usuario_destinatario == remitente.id_usuario:
        raise BadRequest("No puedes enviarte mensajes a ti mismo")
    destinatario = db.get(Usuario, mensaje_in.id_usuario_destinatario)
    if destinatario is None or not destinatario.activo:
        raise NotFound("Destinatario no encontrado")
    if remitente.rol == "cliente" and destinatario.rol == "cliente":
        raise Forbidden("Los clientes solo pueden escribir a veterinarias o administradores")

    id_veterinaria = mensaje_in.id_veterinaria
    if mensaje_in.id_cita is not None:
        cita = db.get(CitaVeterinaria, mensaje_in.id_cita)
        if cita is None or not (es_duenio(cita, remitente) or es_veterinaria(cita, remitente)):
            raise NotFound("Cita no encontrada")
        id_veterinaria = id_veterinaria or cita.id_veterinaria
    if id_veterinaria is not None:
        get_veterinaria_activa(db, id_veterinaria)

    mensaje = Mensaje(
        id_usuario_remitente=remitente.id_usuario,
        id_usuario_destinatario=destinatario.id_usuario,
        id_veterinaria=id_veterinaria,
        id_cita=mensaje_in.id_cita,
        contenido=mensaje_in.contenido,
    )
    return save(db, mensaje)


def list_recibidos(db: Session, id_usuario: int, page: Pagination, solo_no_leidos: bool = False) -> list[Mensaje]:
    stmt = select(Mensaje).where(Mensaje.id_usuario_destinatario == id_usuario).order_by(Mensaje.fecha_envio.desc())
    if solo_no_leidos:
        stmt = stmt.where(Mensaje.leido.is_(False))
    return list(db.scalars(paginate(stmt, page)))


def list_enviados(db: Session, id_usuario: int, page: Pagination) -> list[Mensaje]:
    stmt = select(Mensaje).where(Mensaje.id_usuario_remitente == id_usuario).order_by(Mensaje.fecha_envio.desc())
    return list(db.scalars(paginate(stmt, page)))


def list_conversacion(db: Session, id_usuario: int, id_otro: int, page: Pagination) -> list[Mensaje]:
    stmt = (
        select(Mensaje)
        .where(
            or_(
                and_(Mensaje.id_usuario_remitente == id_usuario, Mensaje.id_usuario_destinatario == id_otro),
                and_(Mensaje.id_usuario_remitente == id_otro, Mensaje.id_usuario_destinatario == id_usuario),
            )
        )
        .order_by(Mensaje.fecha_envio)
    )
    return list(db.scalars(paginate(stmt, page)))


def count_no_leidos(db: Session, id_usuario: int) -> int:
    return db.scalar(
        select(func.count()).where(Mensaje.id_usuario_destinatario == id_usuario, Mensaje.leido.is_(False))
    )


def marcar_leido(db: Session, id_mensaje: int, usuario: Usuario) -> Mensaje:
    mensaje = db.get(Mensaje, id_mensaje)
    if mensaje is None or mensaje.id_usuario_destinatario != usuario.id_usuario:
        raise NotFound("Mensaje no encontrado")
    mensaje.leido = True
    return save(db, mensaje)
