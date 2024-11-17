from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, subject, message, recipient_list, from_email=None, html_message=None):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        self.html_message = html_message

    def send(self):
        """Envia o e-mail com suporte a timeout."""
        try:
            with get_connection(timeout=10) as connection:
                if self.html_message:
                    email = EmailMultiAlternatives(
                        self.subject,
                        self.message,
                        self.from_email,
                        self.recipient_list,
                        connection=connection
                    )
                    email.attach_alternative(self.html_message, "text/html")
                    email.send()
                else:
                    send_mail(
                        self.subject,
                        self.message,
                        self.from_email,
                        self.recipient_list,
                        connection=connection
                    )
            logger.info(f"E-mail enviado com sucesso para {self.recipient_list}")
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {self.recipient_list}: {e}")
            raise e

    def log_to_console(self):
        """Simula o envio de e-mail no console."""
        logger.info(f"E-mail (SIMULAÇÃO) enviado para {self.recipient_list}")
        logger.info(f"Assunto: {self.subject}")
        logger.info(f"Mensagem: {self.message}")
        if self.html_message:
            logger.info(f"Mensagem HTML: {self.html_message}")

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_accounts_task(self, subject, message, recipient_list, from_email=None, html_message=None):
    """Task Celery para envio assíncrono com retries."""
    try:
        email_sender = EmailSender(
            subject=subject,
            message=message,
            recipient_list=recipient_list,
            from_email=from_email,
            html_message=html_message
        )
        if settings.DEBUG:
            logger.info("DEBUG está ativado, simulando envio de e-mail.")
            email_sender.log_to_console()
        else:
            logger.info("Enviando e-mail em produção.")
            email_sender.send()
    except Exception as exc:
        logger.error(f"Erro ao enviar e-mail: {exc}")
        self.retry(exc=exc)
