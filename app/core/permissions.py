from app.models.mascota import Mascota
from app.models.usuario import Usuario
from app.models.veterinaria import Veterinaria


def is_admin(usuario: Usuario) -> bool:
    return usuario.rol == "admin"


def can_manage_veterinaria(usuario: Usuario, veterinaria: Veterinaria) -> bool:
    return is_admin(usuario) or veterinaria.id_usuario == usuario.id_usuario


def can_access_mascota(usuario: Usuario, mascota: Mascota) -> bool:
    return is_admin(usuario) or mascota.id_usuario == usuario.id_usuario
