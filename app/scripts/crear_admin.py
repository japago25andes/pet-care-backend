"""
Convierte un usuario ya registrado en admin.

Uso: docker compose exec api python -m app.scripts.crear_admin correo@ejemplo.com
"""

import sys

from app.crud.usuario import get_usuario_by_correo
from app.database import SessionLocal


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: python -m app.scripts.crear_admin <correo>")
    with SessionLocal() as db:
        usuario = get_usuario_by_correo(db, sys.argv[1])
        if usuario is None:
            sys.exit("No existe un usuario con ese correo. Regístralo primero en POST /auth/register")
        usuario.rol = "admin"
        usuario.activo = True
        db.commit()
        print(f"{usuario.correo_electronico} ahora es admin")


if __name__ == "__main__":
    main()
