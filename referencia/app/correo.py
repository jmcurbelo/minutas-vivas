"""Envío de correo por SMTP. En local apunta a Mailpit (localhost:1025)."""
import smtplib
from email.message import EmailMessage

from .config import Config


def enviar(config: Config, para: str, asunto: str, texto: str) -> None:
    msg = EmailMessage()
    msg["From"] = config.mail_from
    msg["To"] = para
    msg["Subject"] = asunto
    msg.set_content(texto)
    with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=10) as smtp:
        if config.smtp_user:  # proveedor real: cifrado + usuario y contraseña
            smtp.starttls()
            smtp.login(config.smtp_user, config.smtp_password)
        smtp.send_message(msg)
