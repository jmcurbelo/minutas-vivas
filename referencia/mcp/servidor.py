# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=2,<3"]
# ///
"""Servidor MCP de Minutas vivas: Claude consulta los compromisos (solo lectura).

Registrar en Claude Code (desde la carpeta referencia/):
    claude mcp add minutas -- uv run "$(pwd)/mcp/servidor.py"
"""
import os
import sqlite3
from pathlib import Path

from mcp.server.mcpserver import MCPServer

DB = Path(os.environ.get("MINUTAS_DB", Path(__file__).resolve().parent.parent / "minutas.db"))
mcp = MCPServer("minutas")


def conectar() -> sqlite3.Connection:
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)  # solo lectura


@mcp.tool()
def compromisos(estado: str = "Pendiente", responsable: str = "", dias: int = 0) -> str:
    """Lista compromisos con proyecto, responsable y fecha limite.
    estado: 'Pendiente', 'Hecho' o '' para todos. responsable: parte del nombre.
    dias: si es mayor que 0, solo los que vencen en los proximos N dias (incluye vencidos)."""
    sql = ("SELECT c.descripcion, p.nombre, u.nombre, c.fecha_limite, c.estado, "
           "CAST(julianday(c.fecha_limite) - julianday(date('now')) AS INT) AS dias_restantes "
           "FROM compromisos c JOIN proyectos p ON p.id = c.proyecto_id JOIN usuarios u ON u.id = c.responsable_id WHERE 1=1")
    params: list = []
    if estado:
        sql += " AND c.estado = ?"; params.append(estado)
    if responsable:
        sql += " AND u.nombre LIKE ?"; params.append(f"%{responsable}%")
    if dias > 0:
        sql += " AND c.fecha_limite <= date('now', ?)"; params.append(f"+{dias} day")
    sql += " ORDER BY c.fecha_limite"
    with conectar() as con:
        filas = con.execute(sql, params).fetchall()
    if not filas:
        return "Sin resultados."
    return "\n".join(f"- {d} | {p} | {r} | {f} | {e} | {n} dias" for d, p, r, f, e, n in filas)


@mcp.tool()
def consultar(sql: str) -> str:
    """Consulta SQL de solo lectura (SELECT) sobre las tablas usuarios, proyectos y compromisos.
    Nunca devuelve la columna password_hash."""
    if not sql.strip().lower().startswith(("select", "with")) or "password_hash" in sql.lower() or "codigo_hash" in sql.lower():
        return "Solo se permiten SELECT y sin columnas de contraseñas o codigos."
    with conectar() as con:
        cur = con.execute(sql)
        cols = [c[0] for c in cur.description]
        filas = cur.fetchmany(200)
    return "\n".join([" | ".join(cols)] + [" | ".join(str(v) for v in f) for f in filas])


if __name__ == "__main__":
    mcp.run()
