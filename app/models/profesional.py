from sqlalchemy import Boolean, ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.veterinaria import Veterinaria


class Profesional(Base):
    __tablename__ = "profesionales"

    id_profesional: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_veterinaria: Mapped[int] = mapped_column(ForeignKey("veterinarias.id_veterinaria"), nullable=False, index=True)
    nombre_completo: Mapped[str] = mapped_column(String(100), nullable=False)
    especialidad: Mapped[str | None] = mapped_column(String(50))
    numero_registro_profesional: Mapped[str | None] = mapped_column(String(30))
    telefono: Mapped[str | None] = mapped_column(String(20))
    correo_electronico: Mapped[str | None] = mapped_column(String(100))
    activo: Mapped[bool] = mapped_column(Boolean, server_default=true())

    veterinaria: Mapped[Veterinaria] = relationship()
