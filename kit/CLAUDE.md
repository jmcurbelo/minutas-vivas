# Minutas vivas

Aplicación web para llevar los compromisos que salen de cada reunión: qué se comprometió, de qué proyecto, quién es responsable y para cuándo. El objetivo a medio plazo es comercializarla.

## Sobre quién trabaja aquí
- El dueño del proyecto viene de PowerBuilder y SQL (Azure SQL). Es nuevo en desarrollo web.
- Responde siempre en **español**, explica cada paso en lenguaje sencillo y relaciona los conceptos nuevos con su equivalente en PowerBuilder cuando ayude.
- Antes de cambios grandes, propón un plan corto y espera aprobación.

## Preparar el entorno
Si falta alguna herramienta, usa la skill `preparar-entorno`. La lista está en `Brewfile`.

## Stack (no cambiar sin preguntar)
- Python 3.12+ con **uv** para dependencias (`uv add`, `uv run`). Nunca uses `pip install` directo.
- **FastAPI** + plantillas **Jinja2** (HTML generado en el servidor, sin frameworks de frontend).
- **SQLAlchemy 2** sobre **SQLite** (`minutas.db`). Todo acceso a datos con SQLAlchemy, para poder migrar a Azure SQL cambiando solo `DATABASE_URL`.
- Correo por **SMTP**. En local apunta a Mailpit (`localhost:1025`).
- Configuración en `.env` (nunca se sube a GitHub). Deja siempre un `.env.example` actualizado.

## Reglas de seguridad (obligatorias)
- Contraseñas con **Argon2id** (`argon2-cffi`). Nunca guardar ni registrar contraseñas en claro.
- Códigos de restablecimiento: 6 dígitos con `secrets`, guardados con hash, caducan en 15 minutos, un solo uso, máximo 5 intentos.
- Mismos mensajes de error tanto si el correo existe como si no.
- Cookie de sesión firmada, `HttpOnly`, `SameSite=Lax`.

## Forma de trabajar
- Lee `especificacion.md` antes de construir.
- Escribe **tests con pytest** para cada funcionalidad y ejecútalos (`uv run pytest`) antes de decir que algo está terminado.
- Después de cada avance que funcione, propón un commit con un mensaje claro en español.
- Para arrancar: `uv run uvicorn app.main:app --reload` (Mailpit corre como servicio: `brew services start mailpit`).
