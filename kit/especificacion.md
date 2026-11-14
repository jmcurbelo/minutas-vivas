# Especificación · Minutas vivas (versión 1)

## Objetivo de la versión 1
Una aplicación web local donde un equipo puede crear cuenta, entrar con contraseña segura, recuperar la contraseña por correo y gestionar compromisos por proyecto.

## Tablas
| Tabla | Campos |
|---|---|
| `usuarios` | id, nombre, email (único), password_hash, creado_en |
| `codigos_reset` | id, usuario_id, codigo_hash, expira_en, usado, intentos |
| `proyectos` | id, nombre, cliente |
| `compromisos` | id, proyecto_id, responsable_id, descripcion, fecha_limite, estado (Pendiente/Hecho), creado_por_id, creado_en |

## Pantallas
1. **Crear cuenta**: nombre, correo y contraseña (mínimo 10 caracteres). Al terminar, entra directamente.
2. **Entrar**: correo y contraseña. Error genérico si algo no coincide.
3. **¿Olvidaste tu contraseña?**: pide el correo y envía un código de 6 dígitos.
4. **Nueva contraseña**: correo, código y nueva contraseña.
5. **Compromisos**:
   - Filtro "Míos" / "Todos".
   - Formulario en una línea: descripción, proyecto (se crea si no existe), responsable, fecha límite.
   - Tabla ordenada por fecha; los vencidos se marcan en rojo; casilla para marcar como hecho.
6. **Salir**.

## Seguridad
Ver las reglas obligatorias en `CLAUDE.md`.

## Datos de ejemplo
Un script `scripts/sembrar.py` que crea 3 o 4 usuarios, 3 proyectos y unos 9 compromisos (algunos vencidos y uno hecho).

## Criterios de aceptación
- [ ] `uv run pytest` pasa completo.
- [ ] Puedo crear una cuenta, salir y volver a entrar.
- [ ] La contraseña aparece en la base de datos como `$argon2id$...`.
- [ ] Al pedir un código, llega a Mailpit y me permite cambiar la contraseña una sola vez.
- [ ] Puedo crear un compromiso y marcarlo como hecho.

## Fuera de alcance (próximas versiones)
Actas completas con asistentes, adjuntos, permisos por rol, Azure SQL, dominio propio, correo real, IA que extrae compromisos de un acta.
