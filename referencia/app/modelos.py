"""Tablas de la base de datos (SQLAlchemy). Cambiar de SQLite a Azure SQL no toca este archivo."""
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def ahora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    # Argon2id guarda algoritmo, parámetros, SAL y hash en esta misma cadena
    password_hash: Mapped[str] = mapped_column(String(255))
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=ahora)


class CodigoReset(Base):
    __tablename__ = "codigos_reset"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    codigo_hash: Mapped[str] = mapped_column(String(255))  # el código tampoco se guarda en claro
    expira_en: Mapped[datetime] = mapped_column(DateTime)
    usado: Mapped[bool] = mapped_column(Boolean, default=False)
    intentos: Mapped[int] = mapped_column(Integer, default=0)


class Proyecto(Base):
    __tablename__ = "proyectos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(160))
    cliente: Mapped[str] = mapped_column(String(160), default="")


class Compromiso(Base):
    __tablename__ = "compromisos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    proyecto_id: Mapped[int] = mapped_column(ForeignKey("proyectos.id"))
    responsable_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    descripcion: Mapped[str] = mapped_column(Text)
    fecha_limite: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), default="Pendiente")  # Pendiente | Hecho
    creado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=ahora)

    proyecto: Mapped[Proyecto] = relationship()
    responsable: Mapped[Usuario] = relationship(foreign_keys=[responsable_id])
