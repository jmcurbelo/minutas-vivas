"""Configuración leída de variables de entorno (o de un archivo .env)."""
import os
from dataclasses import dataclass
from pathlib import Path


def _cargar_env(ruta: Path = Path(".env")) -> None:
    """Lee un .env sencillo (CLAVE=valor) sin pisar variables ya definidas."""
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip())


@dataclass(frozen=True)
class Config:
    database_url: str
    secret_key: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    mail_from: str


def cargar_config() -> Config:
    _cargar_env()
    return Config(
        database_url=os.environ.get("DATABASE_URL", "sqlite:///minutas.db"),
        secret_key=os.environ.get("SECRET_KEY", "solo-para-desarrollo-local"),
        smtp_host=os.environ.get("SMTP_HOST", "localhost"),
        smtp_port=int(os.environ.get("SMTP_PORT", "1025")),
        smtp_user=os.environ.get("SMTP_USER", ""),
        smtp_password=os.environ.get("SMTP_PASSWORD", ""),
        mail_from=os.environ.get("MAIL_FROM", "Minutas Vivas <no-responder@minutas.local>"),
    )
