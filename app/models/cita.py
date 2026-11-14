from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mascota import Mascota
from app.models.profesional import Profesional
from app.models.veterinaria import Veterinaria


class CitaVeterinaria(Base):
    __tablename__ = "citas_veterinarias"

    id_cita: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_mascota: Mapped[int] = mapped_column(ForeignKey("mascotas.id_mascota"), nullable=False, index=True)
    id_profesional: Mapped[int] = mapped_column(ForeignKey("profesionales.id_profesional"), nullable=False, index=True)
    id_veterinaria: Mapped[int] = mapped_column(ForeignKey("veterinarias.id_veterinaria"), nullable=False, index=True)
    fecha_cita: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    motivo: Mapped[str] = mapped_column(String(200), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), server_default="programada")
    notas: Mapped[str | None] = mapped_column(Text)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    mascota: Mapped[Mascota] = relationship()
    profesional: Mapped[Profesional] = relationship()
    veterinaria: Mapped[Veterinaria] = relationship()

    @property
    def nombre_mascota(self) -> str:
        return self.mascota.nombre

    @property
    def especie_mascota(self) -> str:
        return self.mascota.especie

    @property
    def alergias(self) -> str | None:
        return self.mascota.alergias

    @property
    def condiciones_medicas(self) -> str | None:
        return self.mascota.condiciones_medicas

    @property
    def id_usuario_dueno(self) -> int:
        return self.mascota.id_usuario

    @property
    def nombre_dueno(self) -> str:
        return self.mascota.dueno.nombre_completo

    @property
    def nombre_profesional(self) -> str:
        return self.profesional.nombre_completo

    @property
    def id_usuario_veterinaria(self) -> int:
        return self.veterinaria.id_usuario

    @property
    def nombre_veterinaria(self) -> str:
        return self.veterinaria.nombre_comercial
