# PeludOS API

Backend de la plataforma de cuidado de mascotas: FastAPI + PostgreSQL + SQLAlchemy 2 + Alembic, con autenticación JWT.

## Arranque

```bash
cp .env.example .env        # completa SECRET_KEY y la clave de Postgres
docker compose up -d --build
```

- La API aplica las migraciones al arrancar.
- Swagger: `http://localhost:8000/docs` (ReDoc en `/redoc`). Si el puerto 8000 está ocupado (pasa en Windows), pon `API_PORT=8001` en `.env`.
- Para crear un admin, primero registra el usuario y luego ejecuta: `docker compose exec api python -m app.scripts.crear_admin correo@ejemplo.com`.
- Para crear una migración nueva: `docker compose exec api alembic revision --autogenerate -m "descripcion"`.

## Reglas generales

- **Auth:** `POST /auth/login` (form OAuth2, `username` = correo) devuelve un JWT. Se envía como `Authorization: Bearer <token>`.
- **Roles:**
  - `cliente`: es el rol por defecto.
  - `veterinaria`: gestiona las veterinarias de las que es responsable.
  - `admin`: puede hacerlo todo.
- **Borrado lógico:** los `DELETE` marcan `activo=false`. La única excepción son las vacunas, que se borran definitivamente.
- **PATCH parcial:** solo cambia los campos enviados. Mandar `null` en un campo obligatorio devuelve 422.
- **Paginación:** `limit` (1-100, por defecto 50) y `offset` en los listados.
- **Errores:** siempre con la forma `{"detail": "..."}`.

| Código | Significado |
|---|---|
| 400 | Regla de negocio |
| 401 | Sin token o token inválido |
| 403 | Sin permiso |
| 404 | No existe o no es tuyo |
| 409 | Duplicado, sin stock o estado inválido |
| 422 | Validación |

## Endpoints

🔓 público · 🔑 cualquier usuario autenticado · 🏥 responsable de la veterinaria o admin · 👑 admin

### Autenticación y usuarios
| Método | Ruta | Quién | Comportamiento |
|---|---|---|---|
| POST | `/auth/register` | 🔓 | Crea un `cliente` o una `veterinaria`. El correo se guarda en minúsculas y es único (409). |
| POST | `/auth/login` | 🔓 | Devuelve el JWT. 401 si las credenciales son malas, 403 si el usuario está inactivo. |
| GET / PATCH | `/usuarios/me` | 🔑 | Ver o editar mi perfil (nombre, teléfono, dirección). |
| PUT | `/usuarios/me/contrasena` | 🔑 | Pide la contraseña actual (400 si no coincide). |
| DELETE | `/usuarios/me` | 🔑 | Desactiva la cuenta y el token deja de servir. |
| GET | `/usuarios` | 👑 | Lista con filtros `rol` y `q`. |
| GET / PATCH | `/usuarios/{id}` | 👑 | Cambia `rol` o `activo`. Un admin no puede quitarse su propio rol. |

### Mascotas
| Método | Ruta | Quién | Comportamiento |
|---|---|---|---|
| POST | `/mascotas` | 🔑 | La mascota queda a nombre del usuario. El chip es único entre mascotas activas (409). |
| GET | `/mascotas` | 🔑 | Lista mis mascotas activas. |
| GET / PATCH | `/mascotas/{id}` | 🔑 | Solo el dueño (o un admin). Para cualquier otro devuelve 404. |
| DELETE | `/mascotas/{id}` | 🔑 | Libera el chip, cancela las citas futuras y desactiva los recordatorios. |

### Veterinarias y profesionales
| Método | Ruta | Quién | Comportamiento |
|---|---|---|---|
| GET | `/veterinarias` | 🔓 | Solo las activas. Con `q` busca por nombre. Con `lat`, `lng` y `radio_km` (por defecto 10) devuelve las cercanas con `distancia_km`. Sin coordenadas ordena por calificación. |
| GET | `/veterinarias/mias` | 🏥 | Las mías, incluidas las inactivas. |
| POST | `/veterinarias` | 🏥 | Quien la crea queda como responsable. |
| GET | `/veterinarias/{id}` | 🔓 | Devuelve 404 si está inactiva. |
| PATCH / DELETE | `/veterinarias/{id}` | 🏥 | Solo un admin puede cambiar `activo`. Al desactivarla sale de la búsqueda y de la tienda. |
| GET | `/veterinarias/{id}/profesionales` | 🔓 | Lista los profesionales activos. |
| POST | `/veterinarias/{id}/profesionales` | 🏥 | Agrega un profesional. |
| GET | `/profesionales/{id}` | 🔓 | Ver un profesional. |
| PATCH / DELETE | `/profesionales/{id}` | 🏥 | Al desactivarlo ya no recibe citas nuevas. |

### Citas
| Método | Ruta | Quién | Comportamiento |
|---|---|---|---|
| POST | `/citas` | 🔑 | Para una mascota propia y un profesional activo. La veterinaria se toma del profesional. La fecha debe ser futura (400). Si el profesional ya tiene una cita a esa hora devuelve 409. |
| GET | `/citas` | 🔑 | Citas de mis mascotas más las de mis veterinarias. Filtros: `estado`, `desde`, `hasta`. |
| GET | `/citas/{id}` | 🔑 | Solo para los participantes. |
| PATCH | `/citas/{id}` | 🔑 | Solo si está `programada` o `confirmada`. Cambiar la fecha la vuelve a `programada`. Las `notas` solo las escribe la veterinaria. |
| PATCH | `/citas/{id}/estado` | 🔑 | Ver el flujo de estados abajo. El dueño solo puede cancelar. |

Flujo de estados: `programada → confirmada | cancelada` y `confirmada → completada | cancelada | no_asistio`.

### Salud: recordatorios, medicamentos y vacunas
Todos estos endpoints son 🔑 y solo los usa el dueño de la mascota.

| Método | Ruta | Comportamiento |
|---|---|---|
| GET / POST | `/mascotas/{id}/recordatorios` | `tipo` y `frecuencia` (`unica`, `diaria`, `semanal`, `mensual`, `anual`). |
| GET | `/recordatorios` | Todos los míos. `pendientes=true` muestra los vencidos sin notificar. `hasta` filtra por fecha. |
| GET / PATCH / DELETE | `/recordatorios/{id}` | Cambiar `fecha_programada` lo vuelve a dejar pendiente. |
| POST | `/recordatorios/{id}/notificado` | Guarda `fecha_notificacion`. Si es recurrente avanza a la siguiente fecha (31-ene → 28-feb). |
| GET / POST | `/mascotas/{id}/medicamentos` | `fecha_fin ≥ fecha_inicio`. `solo_vigentes=true` filtra los vigentes hoy. |
| GET / PATCH / DELETE | `/medicamentos/{id}` | Ver, editar o desactivar. |
| GET / POST | `/mascotas/{id}/vacunas` | `fecha_aplicacion` no puede ser futura y `fecha_proxima_dosis` debe ser posterior. |
| GET / PATCH / DELETE | `/vacunas/{id}` | El DELETE es definitivo. |

El `id_recordatorio` de un medicamento o una vacuna debe pertenecer a la misma mascota (400 si no).

### Tienda: productos, carrito y pedidos
| Método | Ruta | Quién | Comportamiento |
|---|---|---|---|
| GET | `/productos` | 🔓 | Catálogo con filtros `id_veterinaria`, `categoria`, `q` y `con_stock`. Nunca muestra `precio_compra`. |
| GET | `/productos/{id}` | 🔓 | Solo si el producto y su veterinaria están activos. |
| GET | `/veterinarias/{id}/inventario` | 🏥 | Incluye inactivos y `precio_compra`. |
| POST | `/veterinarias/{id}/productos` | 🏥 | Crea un producto. |
| PATCH / DELETE | `/productos/{id}` | 🏥 | Editar precio o stock, o desactivar. |
| GET | `/carrito` | 🔑 | Lo crea si no existe y actualiza los precios al precio de venta vigente. |
| POST | `/carrito/items` | 🔑 | Si el producto ya está, suma la cantidad. 409 si supera el stock o si el producto es de otra veterinaria (un carrito solo admite una veterinaria). |
| PATCH / DELETE | `/carrito/items/{id}` | 🔑 | Cambiar la cantidad o quitar el producto. |
| DELETE | `/carrito` | 🔑 | Vacía el carrito. |
| POST | `/pedidos` | 🔑 | Checkout: valida el stock bloqueando las filas, descuenta stock, fija el total, cierra el carrito y crea el pedido `pendiente`. Si no envías `direccion_entrega` usa la del perfil. No procesa pagos. |
| GET | `/pedidos` | 🔑 | Mis compras más los pedidos de mis veterinarias. Filtro: `estado`. |
| GET | `/pedidos/{id}` | 🔑 | Solo para el comprador o la veterinaria. |
| PATCH | `/pedidos/{id}/estado` | 🔑 | Ver el flujo de estados abajo. El comprador solo puede cancelar si está `pendiente`. Cancelar devuelve el stock. |

Flujo de estados: `pendiente → confirmado | cancelado`, `confirmado → enviado | cancelado` y `enviado → entregado` (guarda `fecha_entrega`).

### Reseñas
| Método | Ruta | Quién | Comportamiento |
|---|---|---|---|
| GET | `/veterinarias/{id}/resenas` | 🔓 | Las más recientes primero. |
| POST | `/veterinarias/{id}/resenas` | 🔑 | Calificación de 1 a 5. Una reseña activa por usuario y veterinaria (409). No se puede reseñar la propia (403). `id_pedido` es opcional y debe ser un pedido propio y entregado. |
| PATCH | `/resenas/{id}` | 🔑 | Solo el autor. |
| DELETE | `/resenas/{id}` | 🔑 | El autor o un admin. |

Crear, editar o borrar una reseña recalcula `calificacion_promedio` de la veterinaria.

### Mensajería
| Método | Ruta | Comportamiento |
|---|---|---|
| POST | `/mensajes` | 🔑 Un cliente solo puede escribir a usuarios `veterinaria` o `admin`. Con `id_cita` debes ser parte de la cita, y la veterinaria se completa sola. |
| GET | `/mensajes/recibidos` | 🔑 Filtro `solo_no_leidos`. |
| GET | `/mensajes/enviados` | 🔑 Mensajes que envié. |
| GET | `/mensajes/no-leidos` | 🔑 Devuelve `{"total": n}`. |
| GET | `/mensajes/conversacion/{id_usuario}` | 🔑 Ambos sentidos, en orden cronológico. |
| PATCH | `/mensajes/{id}/leido` | 🔑 Solo el destinatario. |

## Cambios respecto al modelo ER

- `veterinarias.id_usuario` es nuevo: guarda quién es el responsable. Sin este campo nadie podría gestionar una veterinaria.
- El chip de las mascotas es único solo entre mascotas activas (índice parcial).
- Restricciones nuevas en la base:
  - Un solo carrito activo por usuario.
  - Una reseña activa por usuario y veterinaria.
  - Un pedido por carrito.
  - `stock ≥ 0`, `cantidad > 0` y `calificacion` entre 1 y 5.
- Se ignoraron las dos últimas `Ref` del DBML (`pedidos.id_carrito <> pedidos.total` y `profesionales ?<? vacunas.fecha_creacion`) porque no son relaciones válidas.
