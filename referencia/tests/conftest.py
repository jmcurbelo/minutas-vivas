import pytest
from fastapi.testclient import TestClient

from app.config import Config
from app.main import create_app


@pytest.fixture
def buzon():
    """Sustituye al servidor de correo: guarda los mensajes en una lista."""
    return []


@pytest.fixture
def cliente(tmp_path, buzon):
    config = Config(database_url=f"sqlite:///{tmp_path / 'test.db'}", secret_key="test",
                    smtp_host="", smtp_port=0, smtp_user="", smtp_password="", mail_from="test@local")
    app = create_app(config, enviar_correo=lambda para, asunto, texto: buzon.append((para, asunto, texto)))
    with TestClient(app) as c:
        yield c


def registrar(cliente, email="ana@ejemplo.com", password="una-clave-larga", nombre="Ana"):
    return cliente.post("/registro", data={"nombre": nombre, "email": email, "password": password})
