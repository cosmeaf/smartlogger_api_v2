# middleware/allowed_hosts_logger.py
import logging
from django.core.exceptions import DisallowedHost

logger = logging.getLogger(__name__)

class AllowedHostsLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except DisallowedHost as e:
            logger.warning(f"Tentativa de acesso com host inválido: {request.get_host()}")
            raise e
