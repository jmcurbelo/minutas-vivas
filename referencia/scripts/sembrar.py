"""Llena minutas.db con datos de ejemplo para la demo.

Uso:  uv run python scripts/sembrar.py
Usuarios creados (contraseña para todos: demo-minutas-2026):
  sergio@demo.local, laura@demo.local, carlos@demo.local, marta@demo.local
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import seguridad
from app.config import cargar_config
from app.modelos import Base, Compromiso, Proyecto, Usuario

PASSWORD = "demo-minutas-2026"


def main() -> None:
    config = cargar_config()
    if config.database_url.startswith("sqlite:///"):
        Path(config.database_url.removeprefix("sqlite:///")).unlink(missing_ok=True)
    engine = create_engine(config.database_url)
    Base.metadata.create_all(engine)
    hoy = date.today()
    with Session(engine) as s:
        h = seguridad.hashear(PASSWORD)
        personas = [Usuario(nombre=n, email=e, password_hash=h) for n, e in [
            ("Sergio", "sergio@demo.local"), ("Laura", "laura@demo.local"),
            ("Carlos", "carlos@demo.local"), ("Marta", "marta@demo.local")]]
        proyectos = [Proyecto(nombre=n, cliente=c) for n, c in [
            ("Nave Logística Apodaca", "Logística del Norte"), ("Planta Autopartes Saltillo", "Autopartes Cumbres"),
            ("Centro de distribución Laredo", "Lone Star Distribution")]]
        s.add_all(personas + proyectos)
        s.flush()
        sergio, laura, carlos, marta = personas
        apodaca, saltillo, laredo = proyectos
        datos = [
            (apodaca, laura, "Enviar planos de taller revisados al cliente", -2, "Pendiente"),
            (apodaca, carlos, "Confirmar fecha de grúa para el montaje de marcos", 1, "Pendiente"),
            (apodaca, sergio, "Aprobar estimación 3 del subcontratista de montaje", 3, "Pendiente"),
            (saltillo, marta, "Solicitar certificados de calidad del acero", -5, "Hecho"),
            (saltillo, sergio, "Revisar extra por cambio de anclas en eje 4", 0, "Pendiente"),
            (saltillo, laura, "Actualizar programa de fabricación", 6, "Pendiente"),
            (laredo, carlos, "Cotizar transporte de embarques a Texas", 2, "Pendiente"),
            (laredo, marta, "Liberar inspección de pintura (espesor)", -1, "Pendiente"),
            (laredo, sergio, "Firmar contrato de subcontrato de lámina", 9, "Pendiente"),
        ]
        for proyecto, resp, desc, dias, estado in datos:
            s.add(Compromiso(proyecto_id=proyecto.id, responsable_id=resp.id, descripcion=desc,
                             fecha_limite=hoy + timedelta(days=dias), estado=estado, creado_por_id=sergio.id))
        s.commit()
    print(f"Listo. Entra con sergio@demo.local / {PASSWORD}")


if __name__ == "__main__":
    main()
