# Minutas vivas · versión de referencia

Aplicación web para llevar los **compromisos de cada reunión**: quién, qué, de qué proyecto y para cuándo. Incluye cuentas de usuario con contraseñas seguras y restablecimiento por correo.

## Arquitectura

```
Navegador ──► http://localhost:8000 ──► App FastAPI (Python)
                                          ├── SQLite (minutas.db)
                                          └── SMTP ──► Mailpit (http://localhost:8025)
Claude Code ──► servidor MCP (solo lectura) ──► minutas.db
```

| Pieza | Hoy (local) | En producción |
|---|---|---|
| Base de datos | SQLite, un archivo | Azure SQL: cambia `DATABASE_URL` |
| Correo | Mailpit, buzón local | Proveedor SMTP real: cambia `SMTP_*` |
| Dirección | localhost:8000 | Dominio propio con HTTPS |

## Seguridad
- Contraseñas con **Argon2id**: cada una con su **sal** aleatoria, guardada dentro del hash (`$argon2id$...`).
- Código de restablecimiento de 6 dígitos: **guardado con hash**, caduca en 15 minutos, un solo uso y máximo 5 intentos.
- No revela si un correo está registrado.
- Sesión en cookie firmada, `HttpOnly` y `SameSite=Lax`.

## Arrancar (Mac)

```bash
brew install uv mailpit
brew services start mailpit               # bandeja en http://localhost:8025
cp .env.example .env
uv run python scripts/sembrar.py          # datos de ejemplo
uv run uvicorn app.main:app --reload      # http://localhost:8000
```

Usuario de ejemplo: `sergio@demo.local` · contraseña `demo-minutas-2026`

## Tests

```bash
uv run pytest
```

15 pruebas: registro, hash y sal, login, restablecimiento, caducidad, reutilización, límite de intentos y compromisos.

## Conectar Claude (MCP)

```bash
claude mcp add minutas -- uv run "$(pwd)/mcp/servidor.py"
```

Luego pregúntale a Claude: *"¿Qué compromisos vencen esta semana y de quién son?"*
