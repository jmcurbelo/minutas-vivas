"""Minutas vivas: aplicación web (FastAPI) con login seguro y compromisos por proyecto.

Arrancar en local:  uv run uvicorn app.main:app --reload
"""
from datetime import date, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from starlette.middleware.sessions import SessionMiddleware

from . import correo, seguridad
from .config import Config, cargar_config
from .modelos import Base, CodigoReset, Compromiso, Proyecto, Usuario, ahora

AQUI = Path(__file__).parent
MINUTOS_CODIGO = 15
MAX_INTENTOS = 5
MENSAJE_OLVIDE = "Si el correo está registrado, te enviamos un código de 6 dígitos. Revisa tu bandeja."


def create_app(config: Config | None = None, enviar_correo=None) -> FastAPI:
    config = config or cargar_config()
    enviar_correo = enviar_correo or (lambda para, asunto, texto: correo.enviar(config, para, asunto, texto))

    conectar = {"check_same_thread": False} if config.database_url.startswith("sqlite") else {}
    engine = create_engine(config.database_url, connect_args=conectar)
    Base.metadata.create_all(engine)
    SesionBD = sessionmaker(engine, expire_on_commit=False)

    app = FastAPI(title="Minutas vivas")
    # Cookie de sesión firmada, inaccesible desde JavaScript (HttpOnly) y con SameSite=Lax
    app.add_middleware(SessionMiddleware, secret_key=config.secret_key, same_site="lax", https_only=False)
    app.mount("/static", StaticFiles(directory=AQUI / "static"), name="static")
    plantillas = Jinja2Templates(directory=AQUI / "templates")
    app.state.engine = engine

    def bd():
        with SesionBD() as s:
            yield s

    def usuario_actual(request: Request, s: Session) -> Usuario | None:
        uid = request.session.get("uid")
        return s.get(Usuario, uid) if uid else None

    def pagina(request: Request, plantilla: str, **ctx):
        return plantillas.TemplateResponse(request, plantilla, ctx)

    def ir(url: str) -> RedirectResponse:
        return RedirectResponse(url, status_code=303)

    # ---------- Inicio ----------
    @app.get("/")
    def inicio(request: Request, s: Session = Depends(bd)):
        return ir("/compromisos" if usuario_actual(request, s) else "/login")

    # ---------- Registro ----------
    @app.get("/registro", response_class=HTMLResponse)
    def ver_registro(request: Request):
        return pagina(request, "registro.html")

    @app.post("/registro", response_class=HTMLResponse)
    def registrar(request: Request, nombre: str = Form(...), email: str = Form(...),
                  password: str = Form(...), s: Session = Depends(bd)):
        email = email.strip().lower()
        error = seguridad.validar_password(password)
        if not error and s.scalar(select(Usuario).where(Usuario.email == email)):
            error = "Ya existe una cuenta con ese correo."
        if error:
            return pagina(request, "registro.html", error=error, nombre=nombre, email=email)
        u = Usuario(nombre=nombre.strip(), email=email, password_hash=seguridad.hashear(password))
        s.add(u)
        s.commit()
        request.session["uid"] = u.id
        return ir("/compromisos")

    # ---------- Login / logout ----------
    @app.get("/login", response_class=HTMLResponse)
    def ver_login(request: Request):
        return pagina(request, "login.html", aviso=request.query_params.get("aviso"))

    @app.post("/login", response_class=HTMLResponse)
    def login(request: Request, email: str = Form(...), password: str = Form(...), s: Session = Depends(bd)):
        u = s.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))
        if not u or not seguridad.verificar(u.password_hash, password):
            # mismo mensaje en ambos casos: no revelamos si el correo existe
            return pagina(request, "login.html", error="Correo o contraseña incorrectos.", email=email)
        request.session.clear()
        request.session["uid"] = u.id
        return ir("/compromisos")

    @app.post("/logout")
    def logout(request: Request):
        request.session.clear()
        return ir("/login")

    # ---------- Olvidé mi contraseña ----------
    @app.get("/olvide", response_class=HTMLResponse)
    def ver_olvide(request: Request):
        return pagina(request, "olvide.html")

    @app.post("/olvide")
    def olvide(request: Request, email: str = Form(...), s: Session = Depends(bd)):
        email = email.strip().lower()
        u = s.scalar(select(Usuario).where(Usuario.email == email))
        if u:
            for viejo in s.scalars(select(CodigoReset).where(CodigoReset.usuario_id == u.id, CodigoReset.usado.is_(False))):
                viejo.usado = True  # solo vale el último código
            codigo = seguridad.generar_codigo()
            s.add(CodigoReset(usuario_id=u.id, codigo_hash=seguridad.hashear(codigo),
                              expira_en=ahora() + timedelta(minutes=MINUTOS_CODIGO)))
            s.commit()
            enviar_correo(u.email, "Tu código para restablecer la contraseña",
                          f"Hola {u.nombre}:\n\nTu código es {codigo}.\n"
                          f"Caduca en {MINUTOS_CODIGO} minutos y solo se puede usar una vez.\n\n"
                          "Si no lo pediste, ignora este correo.")
        request.session["aviso"] = MENSAJE_OLVIDE
        return ir(f"/restablecer?email={email}")

    @app.get("/restablecer", response_class=HTMLResponse)
    def ver_restablecer(request: Request):
        return pagina(request, "restablecer.html", email=request.query_params.get("email", ""),
                      aviso=request.session.pop("aviso", None))

    @app.post("/restablecer", response_class=HTMLResponse)
    def restablecer(request: Request, email: str = Form(...), codigo: str = Form(...),
                    password: str = Form(...), s: Session = Depends(bd)):
        email = email.strip().lower()
        error_generico = "Código inválido o caducado. Pide uno nuevo."
        u = s.scalar(select(Usuario).where(Usuario.email == email))
        reg = None
        if u:
            reg = s.scalar(select(CodigoReset).where(CodigoReset.usuario_id == u.id, CodigoReset.usado.is_(False))
                           .order_by(CodigoReset.id.desc()))
        if not reg or reg.expira_en < ahora() or reg.intentos >= MAX_INTENTOS:
            return pagina(request, "restablecer.html", email=email, error=error_generico)
        if not seguridad.verificar(reg.codigo_hash, codigo.strip()):
            reg.intentos += 1
            s.commit()
            return pagina(request, "restablecer.html", email=email, error=error_generico)
        error = seguridad.validar_password(password)
        if error:
            return pagina(request, "restablecer.html", email=email, error=error)
        u.password_hash = seguridad.hashear(password)
        reg.usado = True
        s.commit()
        return ir("/login?aviso=Contraseña actualizada. Ya puedes entrar.")

    # ---------- Compromisos ----------
    @app.get("/compromisos", response_class=HTMLResponse)
    def ver_compromisos(request: Request, s: Session = Depends(bd)):
        u = usuario_actual(request, s)
        if not u:
            return ir("/login")
        filtro = request.query_params.get("ver", "mios")
        q = select(Compromiso).order_by(Compromiso.estado.desc(), Compromiso.fecha_limite)
        if filtro == "mios":
            q = q.where(Compromiso.responsable_id == u.id)
        return pagina(request, "compromisos.html", usuario=u, filtro=filtro, hoy=date.today(),
                      compromisos=s.scalars(q).all(),
                      proyectos=s.scalars(select(Proyecto).order_by(Proyecto.nombre)).all(),
                      usuarios=s.scalars(select(Usuario).order_by(Usuario.nombre)).all())

    @app.post("/compromisos")
    def crear_compromiso(request: Request, descripcion: str = Form(...), proyecto: str = Form(...),
                         responsable_id: int = Form(...), fecha_limite: date = Form(...), s: Session = Depends(bd)):
        u = usuario_actual(request, s)
        if not u:
            return ir("/login")
        nombre = proyecto.strip()
        p = s.scalar(select(Proyecto).where(Proyecto.nombre == nombre))
        if not p:
            p = Proyecto(nombre=nombre)
            s.add(p)
            s.flush()
        s.add(Compromiso(proyecto_id=p.id, responsable_id=responsable_id, descripcion=descripcion.strip(),
                         fecha_limite=fecha_limite, creado_por_id=u.id))
        s.commit()
        return ir("/compromisos?ver=todos")

    @app.post("/compromisos/{cid}/hecho")
    def marcar_hecho(cid: int, request: Request, ver: str = Form("mios"), s: Session = Depends(bd)):
        u = usuario_actual(request, s)
        if not u:
            return ir("/login")
        c = s.get(Compromiso, cid)
        if c:
            c.estado = "Pendiente" if c.estado == "Hecho" else "Hecho"
            s.commit()
        return ir(f"/compromisos?ver={'todos' if ver == 'todos' else 'mios'}")

    return app


app = create_app()
