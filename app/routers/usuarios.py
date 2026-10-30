from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.deps import DB, Admin, CurrentUser, Page
from app.core.docs import errores
from app.core.errors import BadRequest, NotFound
from app.core.security import hash_password, verify_password
from app.crud import base
from app.crud import usuario as usuario_crud
from app.models.usuario import Usuario
from app.schemas.common import RolUsuario
from app.schemas.usuario import CambioContrasena, UsuarioAdminUpdate, UsuarioOut, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"], responses=errores(401))


@router.get("/me", response_model=UsuarioOut, summary="Mi perfil")
def read_current_user(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UsuarioOut, summary="Editar mi perfil")
def update_current_user(usuario_in: UsuarioUpdate, db: DB, current_user: CurrentUser):
    """Solo cambia los campos enviados. El correo y el rol no se editan aquí."""
    return base.update(db, current_user, usuario_in.cambios())


@router.put(
    "/me/contrasena",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cambiar mi contraseña",
    responses=errores(400),
)
def change_password(datos: CambioContrasena, db: DB, current_user: CurrentUser):
    if not verify_password(datos.contrasena_actual, current_user.contrasena_hash):
        raise BadRequest("La contraseña actual no es correcta")
    base.update(db, current_user, {"contrasena_hash": hash_password(datos.contrasena_nueva)})


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar mi cuenta")
def deactivate_current_user(db: DB, current_user: CurrentUser):
    """Baja lógica: el usuario ya no puede iniciar sesión y su token deja de funcionar."""
    base.deactivate(db, current_user)


@router.get("", response_model=list[UsuarioOut], summary="Listar usuarios (admin)", responses=errores(403))
def list_usuarios(
    db: DB,
    _: Admin,
    page: Page,
    rol: RolUsuario | None = None,
    q: Annotated[str | None, Query(description="Busca en nombre o correo")] = None,
):
    return usuario_crud.list_usuarios(db, page, rol=rol, q=q)


@router.get("/{id_usuario}", response_model=UsuarioOut, summary="Ver usuario (admin)", responses=errores(403, 404))
def get_usuario(id_usuario: int, db: DB, _: Admin):
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise NotFound("Usuario no encontrado")
    return usuario


@router.patch(
    "/{id_usuario}",
    response_model=UsuarioOut,
    summary="Cambiar rol o estado (admin)",
    responses=errores(400, 403, 404),
)
def admin_update_usuario(id_usuario: int, usuario_in: UsuarioAdminUpdate, db: DB, admin: Admin):
    """Un admin no puede quitarse su propio rol ni desactivarse."""
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise NotFound("Usuario no encontrado")
    cambios = usuario_in.cambios()
    if usuario.id_usuario == admin.id_usuario and (cambios.get("rol", "admin") != "admin" or cambios.get("activo") is False):
        raise BadRequest("No puedes quitarte el rol admin ni desactivarte")
    return base.update(db, usuario, cambios)
