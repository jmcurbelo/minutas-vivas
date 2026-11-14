from datetime import date, timedelta

from tests.conftest import registrar


def test_crear_y_marcar_compromiso(cliente):
    registrar(cliente)
    r = cliente.post("/compromisos", data={"descripcion": "Enviar planos revisados", "proyecto": "Nave Apodaca",
                                           "responsable_id": 1, "fecha_limite": date.today().isoformat()})
    assert "Enviar planos revisados" in r.text and "Nave Apodaca" in r.text
    r = cliente.post("/compromisos/1/hecho", data={"ver": "mios"})
    assert 'class="hecho' in r.text


def test_compromiso_vencido_se_marca(cliente):
    registrar(cliente)
    ayer = (date.today() - timedelta(days=1)).isoformat()
    r = cliente.post("/compromisos", data={"descripcion": "Confirmar grúa", "proyecto": "P1",
                                           "responsable_id": 1, "fecha_limite": ayer})
    assert "vencido" in r.text


def test_filtro_mios_y_todos(cliente):
    registrar(cliente, email="ana@x.com", nombre="Ana")
    cliente.post("/logout")
    registrar(cliente, email="luis@x.com", nombre="Luis")
    cliente.post("/compromisos", data={"descripcion": "Tarea de Ana", "proyecto": "P1",
                                       "responsable_id": 1, "fecha_limite": date.today().isoformat()})
    assert "Tarea de Ana" not in cliente.get("/compromisos?ver=mios").text
    assert "Tarea de Ana" in cliente.get("/compromisos?ver=todos").text
