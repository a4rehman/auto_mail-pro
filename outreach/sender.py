import smtplib
from email.message import EmailMessage
from typing import Dict, Any
from config.settings import settings
from core.exceptions import SendError


class EmailSender:
    def __init__(self, dry_run: bool = None):
        self.dry_run = settings.DRY_RUN if dry_run is None else dry_run
    
    def send(self, to_email: str, subject: str, body: str, from_email: str = None) -> Dict[str, Any]:
        if self.dry_run:
            return {"status": "dry_run", "to": to_email, "message": "Email not sent (DRY_RUN)"}
        if not to_email:
            raise SendError("No recipient email")
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = from_email or f"{settings.SENDER_NAME} <{settings.SENDER_EMAIL}>"
            msg['To'] = to_email
            msg.set_content(body)
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
            server.quit()
            return {"status": "success", "to": to_email}
        except Exception as e:
            raise SendError(f"Failed to send email: {e}")
