import re
from datetime import timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modelos import CodigoReset, Usuario, ahora
from tests.conftest import registrar


def codigo_del_correo(buzon):
    return re.search(r"\b(\d{6})\b", buzon[-1][2]).group(1)


def test_registro_guarda_hash_argon2_y_no_la_contrasena(cliente):
    r = registrar(cliente)
    assert r.status_code == 200 and "Compromisos" in r.text
    with Session(cliente.app.state.engine) as s:
        u = s.scalar(select(Usuario))
    assert u.password_hash.startswith("$argon2id$")
    assert "una-clave-larga" not in u.password_hash


def test_misma_contrasena_produce_hashes_distintos_por_la_sal(cliente):
    registrar(cliente, email="a@x.com")
    cliente.post("/logout")
    registrar(cliente, email="b@x.com")
    with Session(cliente.app.state.engine) as s:
        h1, h2 = s.scalars(select(Usuario.password_hash)).all()
    assert h1 != h2


def test_contrasena_corta_rechazada(cliente):
    r = registrar(cliente, password="corta")
    assert "al menos 10 caracteres" in r.text


def test_correo_duplicado_rechazado(cliente):
    registrar(cliente)
    cliente.post("/logout")
    r = registrar(cliente)
    assert "Ya existe una cuenta" in r.text


def test_login_correcto_e_incorrecto(cliente):
    registrar(cliente)
    cliente.post("/logout")
    assert "incorrectos" in cliente.post("/login", data={"email": "ana@ejemplo.com", "password": "mala-clave-xx"}).text
    r = cliente.post("/login", data={"email": "ANA@ejemplo.com ", "password": "una-clave-larga"})
    assert "Compromisos" in r.text


def test_compromisos_requiere_login(cliente):
    r = cliente.get("/compromisos", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/login"


def test_restablecer_flujo_completo(cliente, buzon):
    registrar(cliente)
    cliente.post("/logout")
    r = cliente.post("/olvide", data={"email": "ana@ejemplo.com"})
    assert "te enviamos un código" in r.text
    codigo = codigo_del_correo(buzon)
    r = cliente.post("/restablecer", data={"email": "ana@ejemplo.com", "codigo": codigo, "password": "nueva-clave-segura"})
    assert "Contraseña actualizada" in r.text
    assert "Compromisos" in cliente.post("/login", data={"email": "ana@ejemplo.com", "password": "nueva-clave-segura"}).text


def test_codigo_no_se_puede_reutilizar(cliente, buzon):
    registrar(cliente)
    cliente.post("/olvide", data={"email": "ana@ejemplo.com"})
    codigo = codigo_del_correo(buzon)
    datos = {"email": "ana@ejemplo.com", "codigo": codigo, "password": "nueva-clave-segura"}
    cliente.post("/restablecer", data=datos)
    assert "inválido o caducado" in cliente.post("/restablecer", data=datos).text


def test_codigo_caducado(cliente, buzon):
    registrar(cliente)
    cliente.post("/olvide", data={"email": "ana@ejemplo.com"})
    codigo = codigo_del_correo(buzon)
    with Session(cliente.app.state.engine) as s:
        s.execute(update(CodigoReset).values(expira_en=ahora() - timedelta(minutes=1)))
        s.commit()
    r = cliente.post("/restablecer", data={"email": "ana@ejemplo.com", "codigo": codigo, "password": "nueva-clave-segura"})
    assert "inválido o caducado" in r.text


def test_maximo_cinco_intentos(cliente, buzon):
    registrar(cliente)
    cliente.post("/olvide", data={"email": "ana@ejemplo.com"})
    codigo = codigo_del_correo(buzon)
    malo = "000000" if codigo != "000000" else "111111"
    for _ in range(5):
        cliente.post("/restablecer", data={"email": "ana@ejemplo.com", "codigo": malo, "password": "nueva-clave-segura"})
    r = cliente.post("/restablecer", data={"email": "ana@ejemplo.com", "codigo": codigo, "password": "nueva-clave-segura"})
    assert "inválido o caducado" in r.text


def test_olvide_no_revela_si_el_correo_existe(cliente, buzon):
    r = cliente.post("/olvide", data={"email": "nadie@ejemplo.com"})
    assert "te enviamos un código" in r.text
    assert buzon == []


def test_el_codigo_se_guarda_con_hash(cliente, buzon):
    registrar(cliente)
    cliente.post("/olvide", data={"email": "ana@ejemplo.com"})
    codigo = codigo_del_correo(buzon)
    with Session(cliente.app.state.engine) as s:
        guardado = s.scalar(select(CodigoReset.codigo_hash))
    assert codigo not in guardado and guardado.startswith("$argon2id$")
