from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.deps import Pagination
from app.crud.base import paginate, save
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate


def get_usuario_by_correo(db: Session, correo_electronico: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.correo_electronico == correo_electronico.lower()))


def create_usuario(db: Session, usuario_in: UsuarioCreate, contrasena_hash: str) -> Usuario:
    usuario = Usuario(
        nombre_completo=usuario_in.nombre_completo,
        correo_electronico=usuario_in.correo_electronico,
        contrasena_hash=contrasena_hash,
        telefono=usuario_in.telefono,
        direccion=usuario_in.direccion,
        rol=usuario_in.rol,
    )
    return save(db, usuario)


def list_usuarios(db: Session, page: Pagination, rol: str | None = None, q: str | None = None) -> list[Usuario]:
    stmt = select(Usuario).order_by(Usuario.id_usuario)
    if rol:
        stmt = stmt.where(Usuario.rol == rol)
    if q:
        stmt = stmt.where(
            or_(
                Usuario.nombre_completo.icontains(q, autoescape=True),
                Usuario.correo_electronico.icontains(q, autoescape=True),
            )
        )
    return list(db.scalars(paginate(stmt, page)))
