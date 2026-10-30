from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.core.errors import APIError
from app.routers import (
    auth,
    carrito,
    citas,
    mascotas,
    medicamentos,
    mensajes,
    pedidos,
    productos,
    profesionales,
    recordatorios,
    resenas,
    usuarios,
    vacunas,
    veterinarias,
)

DESCRIPCION = """
API de PeludOS: mascotas, veterinarias, citas, recordatorios de salud, tienda y mensajería.

**Cómo probar aquí:** registra un usuario en `POST /auth/register`, pulsa **Authorize**
y entra con tu correo como *username*. Los endpoints con candado necesitan ese token.

**Roles:** `cliente` (por defecto), `veterinaria` (gestiona sus veterinarias) y `admin` (todo).

**Errores:** siempre `{"detail": "..."}`. 400 regla de negocio · 401 sin token · 403 sin permiso ·
404 no existe o no es tuyo · 409 duplicado/stock/estado · 422 validación.
"""

TAGS = [
    {"name": "Autenticación", "description": "Registro e inicio de sesión (JWT Bearer)."},
    {"name": "Usuarios", "description": "Perfil propio y administración de usuarios."},
    {"name": "Mascotas", "description": "Mascotas del usuario autenticado."},
    {"name": "Veterinarias", "description": "Búsqueda pública (texto y cercanía) y gestión por su responsable."},
    {"name": "Profesionales", "description": "Veterinarios de cada veterinaria."},
    {"name": "Citas", "description": "Agenda entre mascotas y profesionales, con flujo de estados."},
    {"name": "Recordatorios", "description": "Alertas por mascota, únicas o recurrentes."},
    {"name": "Medicamentos", "description": "Tratamientos de cada mascota."},
    {"name": "Vacunas", "description": "Carné de vacunación de cada mascota."},
    {"name": "Productos", "description": "Catálogo público e inventario de cada veterinaria."},
    {"name": "Carrito", "description": "Un carrito activo por usuario, con productos de una sola veterinaria."},
    {"name": "Pedidos", "description": "Checkout del carrito y seguimiento del pedido."},
    {"name": "Reseñas", "description": "Calificaciones de 1 a 5 que alimentan el promedio de la veterinaria."},
    {"name": "Mensajería", "description": "Mensajes directos entre clientes y veterinarias."},
    {"name": "Salud", "description": "Estado del servicio."},
]

app = FastAPI(
    title="PeludOS API",
    description=DESCRIPCION,
    version="1.0.0",
    openapi_tags=TAGS,
    swagger_ui_parameters={"persistAuthorization": True, "docExpansion": "none", "filter": True},
    redoc_url=None,
)

# FastAPI usa redoc@next, cuya versión beta ya no carga como script clásico (página en blanco).
REDOC_JS_URL = "https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js"

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(APIError)
def api_error_handler(_: Request, exc: APIError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(IntegrityError)
def integrity_error_handler(_: Request, exc: IntegrityError):
    # Respaldo ante carreras: la base rechazó un duplicado o una referencia inválida.
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "La operación entra en conflicto con datos existentes"},
    )


for router in (
    auth,
    usuarios,
    mascotas,
    veterinarias,
    profesionales,
    citas,
    recordatorios,
    medicamentos,
    vacunas,
    productos,
    carrito,
    pedidos,
    resenas,
    mensajes,
):
    app.include_router(router.router)


@app.get("/redoc", include_in_schema=False)
def redoc():
    return get_redoc_html(openapi_url=app.openapi_url, title=f"{app.title} - ReDoc", redoc_js_url=REDOC_JS_URL)


@app.get("/health", tags=["Salud"], summary="Health check")
def health_check():
    """Endpoint simple para verificar que la API está corriendo."""
    return {"status": "ok", "app": "PeludOS API"}
