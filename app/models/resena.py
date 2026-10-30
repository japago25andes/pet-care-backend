from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, func, text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.usuario import Usuario


class Resena(Base):
    __tablename__ = "resenas"
    __table_args__ = (
        CheckConstraint("calificacion BETWEEN 1 AND 5", name="ck_resenas_calificacion_rango"),
        # Una reseña activa por usuario y veterinaria.
        Index(
            "uq_resenas_usuario_veterinaria_activa",
            "id_usuario",
            "id_veterinaria",
            unique=True,
            postgresql_where=text("activo"),
        ),
    )

    id_resena: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    id_veterinaria: Mapped[int] = mapped_column(ForeignKey("veterinarias.id_veterinaria"), nullable=False, index=True)
    id_pedido: Mapped[int | None] = mapped_column(ForeignKey("pedidos.id_pedido"))
    calificacion: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    activo: Mapped[bool] = mapped_column(Boolean, server_default=true())

    usuario: Mapped[Usuario] = relationship()

    @property
    def nombre_usuario(self) -> str:
        return self.usuario.nombre_completo
