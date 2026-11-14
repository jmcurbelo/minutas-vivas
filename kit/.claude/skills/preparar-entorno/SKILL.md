---
name: preparar-entorno
description: Revisa e instala en la Mac todo lo que necesita este proyecto (Homebrew, git, uv, Mailpit) y verifica que funciona. Úsala cuando pidan preparar el entorno, instalar dependencias, o cuando un comando falle porque falta una herramienta.
---

# Preparar el entorno de la Mac

Objetivo: dejar la Mac lista para este proyecto, explicando cada herramienta en una frase y sin que la persona tenga que copiar y pegar nada, salvo lo que exija su contraseña.

## Pasos

1. **Diagnóstico.** Ejecuta y muestra una tabla con ✅ / ❌ y la versión:
   - `sw_vers -productVersion` y `uname -m` (versión de macOS y si es Apple Silicon)
   - `brew --version`
   - `git --version`
   - `gh --version` y `gh auth status`
   - `uv --version`
   - `mailpit version`

2. **Homebrew (si falta).** Explica: "Homebrew es el instalador de programas de la Mac, como una tienda de aplicaciones para la terminal".
   - Su instalación **pide la contraseña de la Mac**, y tú no puedes escribirla. Dale a la persona este comando para pegarlo en la app **Terminal**:
     `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
   - Al terminar, Homebrew muestra 2 líneas "Next steps" para añadirlo al PATH. Pídele que las ejecute también, o hazlo tú con su permiso.
   - Espera a que confirme y vuelve a comprobar `brew --version`.

3. **El resto (no pide contraseña).** Desde la raíz del proyecto ejecuta `brew bundle` (lee el `Brewfile`). Explica cada herramienta:
   - **git**: guarda el historial de cambios del código.
   - **gh**: conecta la terminal con la cuenta de GitHub para poder subir el código.
   - **uv**: instala Python y las librerías del proyecto, aisladas del resto de la Mac.
   - **mailpit**: un servidor de correo de mentira para pruebas; los correos se ven en http://localhost:8025.

4. **Verificación final.**
   - Repite el diagnóstico: todo debe salir ✅.
   - Si `git config user.name` está vacío, pregunta nombre y correo y configúralos.
   - Si `gh auth status` indica que no hay sesión, pide a la persona que ejecute en **Terminal** `gh auth login` (GitHub.com → HTTPS → iniciar sesión con el navegador) y después `gh auth setup-git`. Tú no puedes completar ese inicio de sesión por ella.
   - Arranca Mailpit como servicio (`brew services start mailpit`) y confirma que http://localhost:8025 responde.

5. **Cierre.** Resume en 3 líneas qué se instaló y para qué sirve, y sugiere el siguiente paso: "Ya podemos construir la aplicación. Lee `especificacion.md` y propón un plan."

## Reglas
- Pide confirmación antes de instalar cualquier cosa.
- Si algo falla, muestra el error, explica la causa probable en lenguaje sencillo y propone una solución.
- No uses `sudo`.
