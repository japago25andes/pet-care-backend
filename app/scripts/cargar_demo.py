"""
Carga datos de ejemplo para probar el frontend. No hace nada si ya se cargaron.

Uso: docker compose exec api python -m app.scripts.cargar_demo

Usuarios creados (contraseña de todos: Demo12345):
  cliente@peludos.test   cliente con mascotas, citas, recordatorios y pedidos
  vet@peludos.test       responsable de Clínica Patitas
  vet2@peludos.test      responsable de Huellitas Norte
  admin@peludos.test     administrador
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models import (
    CarritoCompras,
    CitaVeterinaria,
    DetalleCarrito,
    Mascota,
    Medicamento,
    Mensaje,
    Pedido,
    Producto,
    Profesional,
    Recordatorio,
    Resena,
    Usuario,
    Vacuna,
    Veterinaria,
)

CONTRASENA = "Demo12345"


def _usuario(nombre: str, correo: str, rol: str, contrasena_hash: str, **extra) -> Usuario:
    return Usuario(nombre_completo=nombre, correo_electronico=correo, rol=rol, contrasena_hash=contrasena_hash, **extra)


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Usuario).where(Usuario.correo_electronico == "cliente@peludos.test")):
            print("Los datos de ejemplo ya estaban cargados")
            return

        ahora = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        hoy = date.today()
        clave = hash_password(CONTRASENA)

        cliente = _usuario(
            "Camila Rojas", "cliente@peludos.test", "cliente", clave,
            telefono="3001234567", direccion="Calle 85 # 15-20, Bogotá",
        )
        vet = _usuario("Andrés Medina", "vet@peludos.test", "veterinaria", clave, telefono="3015551234")
        vet2 = _usuario("Paula Torres", "vet2@peludos.test", "veterinaria", clave, telefono="3025550000")
        admin = _usuario("Admin PeludOS", "admin@peludos.test", "admin", clave)
        db.add_all([cliente, vet, vet2, admin])
        db.flush()

        patitas = Veterinaria(
            id_usuario=vet.id_usuario, nombre_comercial="Clínica Patitas", direccion="Av. 68 # 12-34, Bogotá",
            telefono="6015551234", correo_electronico="contacto@patitas.test", horario_atencion="Lun-Sáb 8:00-18:00",
            latitud=Decimal("4.64828370"), longitud=Decimal("-74.09399460"), calificacion_promedio=Decimal("4.50"),
        )
        huellitas = Veterinaria(
            id_usuario=vet2.id_usuario, nombre_comercial="Huellitas Norte", direccion="Cra. 15 # 124-30, Bogotá",
            telefono="6015550000", horario_atencion="Todos los días 7:00-21:00",
            latitud=Decimal("4.70230000"), longitud=Decimal("-74.04210000"), calificacion_promedio=Decimal("5.00"),
        )
        db.add_all([patitas, huellitas])
        db.flush()

        laura = Profesional(
            id_veterinaria=patitas.id_veterinaria, nombre_completo="Dra. Laura Gómez",
            especialidad="Medicina general", numero_registro_profesional="MV-12345",
        )
        julian = Profesional(
            id_veterinaria=patitas.id_veterinaria, nombre_completo="Dr. Julián Ortiz", especialidad="Dermatología",
        )
        marta = Profesional(
            id_veterinaria=huellitas.id_veterinaria, nombre_completo="Dra. Marta Díaz", especialidad="Cirugía",
        )
        db.add_all([laura, julian, marta])
        db.flush()

        luna = Mascota(
            id_usuario=cliente.id_usuario, nombre="Luna", especie="perro", raza="Labrador", sexo="hembra",
            fecha_nacimiento=date(2021, 5, 10), peso_kg=Decimal("24.50"), color_mascota="Dorado",
            numero_chip="985141000123456", alergias="Pollo", activo=True,
        )
        michi = Mascota(
            id_usuario=cliente.id_usuario, nombre="Michi", especie="gato", raza="Criollo", sexo="macho",
            fecha_nacimiento=date(2023, 2, 1), peso_kg=Decimal("4.20"), color_mascota="Gris",
            condiciones_medicas="Asma leve", activo=True,
        )
        db.add_all([luna, michi])
        db.flush()

        cita_confirmada = CitaVeterinaria(
            id_mascota=luna.id_mascota, id_profesional=laura.id_profesional, id_veterinaria=patitas.id_veterinaria,
            fecha_cita=ahora + timedelta(days=2, hours=3), motivo="Control anual", estado="confirmada",
        )
        db.add_all(
            [
                cita_confirmada,
                CitaVeterinaria(
                    id_mascota=michi.id_mascota, id_profesional=julian.id_profesional,
                    id_veterinaria=patitas.id_veterinaria, fecha_cita=ahora + timedelta(days=6),
                    motivo="Revisión de piel", estado="programada",
                ),
                CitaVeterinaria(
                    id_mascota=luna.id_mascota, id_profesional=laura.id_profesional,
                    id_veterinaria=patitas.id_veterinaria, fecha_cita=ahora - timedelta(days=40),
                    motivo="Vacunación", estado="completada", notas="Sin reacciones. Repetir en un año.",
                ),
            ]
        )
        db.flush()

        pipeta = Recordatorio(
            id_mascota=luna.id_mascota, titulo="Aplicar pipeta antipulgas", tipo="desparasitacion",
            fecha_programada=ahora - timedelta(days=1), frecuencia="mensual",
        )
        bano = Recordatorio(
            id_mascota=michi.id_mascota, titulo="Limpieza de arenero profunda", tipo="higiene",
            fecha_programada=ahora + timedelta(days=4), frecuencia="semanal",
        )
        db.add_all([pipeta, bano])
        db.flush()

        db.add_all(
            [
                Medicamento(
                    id_mascota=luna.id_mascota, nombre_medicamento="Omega 3", dosis="1", unidad_medida="cápsula",
                    frecuencia_administracion="Cada 24 horas", fecha_inicio=hoy - timedelta(days=10),
                    fecha_fin=hoy + timedelta(days=20),
                ),
                Vacuna(
                    id_mascota=luna.id_mascota, nombre_vacuna="Rabia", fecha_aplicacion=hoy - timedelta(days=40),
                    fecha_proxima_dosis=hoy + timedelta(days=325), lote="RB-2291", veterinario_nombre="Dra. Laura Gómez",
                ),
                Vacuna(
                    id_mascota=michi.id_mascota, nombre_vacuna="Triple felina", fecha_aplicacion=hoy - timedelta(days=90),
                    fecha_proxima_dosis=hoy + timedelta(days=275), numero_dosis=2,
                ),
            ]
        )

        concentrado = Producto(
            id_veterinaria=patitas.id_veterinaria, nombre_producto="Concentrado adulto 3 kg", categoria="alimento",
            descripcion="Alimento balanceado para perros adultos.", precio_compra=Decimal("42000"),
            precio_venta=Decimal("58900"), stock=18, unidad_medida="bolsa",
        )
        db.add(concentrado)
        db.add_all(
            [
                Producto(
                    id_veterinaria=patitas.id_veterinaria, nombre_producto="Pipeta antipulgas", categoria="medicamento",
                    precio_compra=Decimal("18000"), precio_venta=Decimal("32000"), stock=25, unidad_medida="unidad",
                ),
                Producto(
                    id_veterinaria=patitas.id_veterinaria, nombre_producto="Shampoo hipoalergénico", categoria="higiene",
                    precio_compra=Decimal("15000"), precio_venta=Decimal("27500"), stock=2, unidad_medida="frasco",
                ),
                Producto(
                    id_veterinaria=huellitas.id_veterinaria, nombre_producto="Collar reflectivo", categoria="accesorio",
                    precio_compra=Decimal("9000"), precio_venta=Decimal("21000"), stock=12, unidad_medida="unidad",
                ),
                Producto(
                    id_veterinaria=huellitas.id_veterinaria, nombre_producto="Pelota mordedera", categoria="juguete",
                    precio_compra=Decimal("6000"), precio_venta=Decimal("14500"), stock=30, unidad_medida="unidad",
                ),
            ]
        )
        db.flush()

        carrito = CarritoCompras(id_usuario=cliente.id_usuario, estado="convertido")
        carrito.detalles.append(
            DetalleCarrito(
                producto=concentrado, cantidad=2, precio_unitario=concentrado.precio_venta,
                subtotal=concentrado.precio_venta * 2,
            )
        )
        db.add(carrito)
        db.flush()
        pedido = Pedido(
            id_usuario=cliente.id_usuario, id_veterinaria=patitas.id_veterinaria, id_carrito=carrito.id_carrito,
            total=concentrado.precio_venta * 2, estado_pedido="entregado", metodo_pago="tarjeta",
            direccion_entrega=cliente.direccion, fecha_entrega=ahora - timedelta(days=5),
        )
        db.add(pedido)
        db.flush()

        db.add_all(
            [
                Resena(
                    id_usuario=cliente.id_usuario, id_veterinaria=patitas.id_veterinaria, id_pedido=pedido.id_pedido,
                    calificacion=5, comentario="Muy buena atención con Luna.",
                ),
                Resena(
                    id_usuario=vet2.id_usuario, id_veterinaria=patitas.id_veterinaria, calificacion=4,
                    comentario="Puntuales y amables.",
                ),
                Resena(
                    id_usuario=vet.id_usuario, id_veterinaria=huellitas.id_veterinaria, calificacion=5,
                    comentario="Abren hasta tarde, muy útil.",
                ),
                Mensaje(
                    id_usuario_remitente=cliente.id_usuario, id_usuario_destinatario=vet.id_usuario,
                    id_veterinaria=patitas.id_veterinaria, id_cita=cita_confirmada.id_cita,
                    contenido="Hola, ¿debo llevar a Luna en ayunas?", leido=True,
                ),
                Mensaje(
                    id_usuario_remitente=vet.id_usuario, id_usuario_destinatario=cliente.id_usuario,
                    id_veterinaria=patitas.id_veterinaria, id_cita=cita_confirmada.id_cita,
                    contenido="No hace falta. Solo trae su carné de vacunas.",
                ),
            ]
        )
        db.commit()
        print("Datos de ejemplo cargados")


if __name__ == "__main__":
    main()
