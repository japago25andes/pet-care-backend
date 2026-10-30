from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import DB
from app.core.docs import errores
from app.core.errors import Conflict, Forbidden
from app.core.security import create_access_token, hash_password, verify_password
from app.crud import usuario as usuario_crud
from app.schemas.usuario import Token, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    responses=errores(409),
)
def register(usuario_in: UsuarioCreate, db: DB):
    """Crea una cuenta `cliente` (por defecto) o `veterinaria`. El correo se guarda en minúsculas y es único."""
    if usuario_crud.get_usuario_by_correo(db, usuario_in.correo_electronico):
        raise Conflict("Ya existe un usuario con ese correo electrónico")
    return usuario_crud.create_usuario(db, usuario_in=usuario_in, contrasena_hash=hash_password(usuario_in.contrasena))


@router.post("/login", response_model=Token, summary="Iniciar sesión", responses=errores(401, 403))
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DB):
    """
    Formulario OAuth2: **username** = correo, **password** = contraseña.
    Devuelve un JWT para el header `Authorization: Bearer <token>`.
    """
    usuario = usuario_crud.get_usuario_by_correo(db, form_data.username.strip())
    if not usuario or not verify_password(form_data.password, usuario.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.activo:
        raise Forbidden("Usuario inactivo")
    return Token(access_token=create_access_token(usuario.id_usuario))
