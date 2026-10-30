from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.errors import Forbidden
from app.core.security import decode_access_token
from app.database import get_db
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

DB = Annotated[Session, Depends(get_db)]


def get_current_user(db: DB, token: Annotated[str, Depends(oauth2_scheme)]) -> Usuario:
    id_usuario = decode_access_token(token)
    usuario = db.get(Usuario, id_usuario) if id_usuario is not None else None
    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def require_roles(*roles: str):
    def dependency(current_user: CurrentUser) -> Usuario:
        if current_user.rol not in roles:
            raise Forbidden("No tienes permisos para esta acción")
        return current_user

    return dependency


Gestor = Annotated[Usuario, Depends(require_roles("veterinaria", "admin"))]
Admin = Annotated[Usuario, Depends(require_roles("admin"))]


class Pagination:
    def __init__(
        self,
        limit: Annotated[int, Query(ge=1, le=100, description="Máximo de resultados")] = 50,
        offset: Annotated[int, Query(ge=0, description="Resultados a saltar")] = 0,
    ):
        self.limit = limit
        self.offset = offset


Page = Annotated[Pagination, Depends()]
