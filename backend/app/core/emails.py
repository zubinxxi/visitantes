import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from app.core.config import settings

def send_email(email_to: str, subject: str, html_content: str):
    """
    Envía un correo electrónico usando la configuración SMTP de settings.
    """
    if not settings.SMTP_HOST:
        print(f"DEBUG: No se envió correo a {email_to} porque SMTP_HOST no está configurado.")
        print(f"Subject: {subject}")
        print(f"Content: {html_content}")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = Header(subject, "utf-8")
    message["From"] = f"{Header(settings.EMAILS_FROM_NAME, 'utf-8')} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = email_to

    part = MIMEText(html_content, "html", "utf-8")
    message.attach(part)

    try:
        if settings.SMTP_SSL:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            if settings.SMTP_TLS:
                server.starttls()
        
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        server.sendmail(settings.EMAILS_FROM_EMAIL, email_to, message.as_string())
        server.quit()
    except Exception as e:
        print(f"Error enviando correo a {email_to}: {e}")
        raise e

def send_reset_password_email(email_to: str, login: str, token: str):
    subject = "Restablecer contraseña - VisitantesDB"
    reset_link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
            <div style="background-color: #0f172a; padding: 20px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0;">VisitantesDB</h1>
            </div>
            <div style="padding: 30px; background-color: #ffffff;">
                <p>Hola <strong>{login}</strong>,</p>
                <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente botón para continuar:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Restablecer Contraseña</a>
                </div>
                <p style="font-size: 14px; color: #64748b;">Este enlace expirará en 15 minutos.</p>
                <p style="font-size: 14px; color: #64748b;">Si no solicitaste este cambio, puedes ignorar este correo.</p>
            </div>
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="font-size: 12px; color: #94a3b8; margin: 0;">&copy; 2026 Autoridad Marítima de Panamá</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(email_to, subject, html_content)
