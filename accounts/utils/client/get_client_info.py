from user_agents import parse
import logging

logger = logging.getLogger(__name__)

def get_client_info(request=None):
    """Obtém informações do cliente a partir do cabeçalho User-Agent."""
    default_info = {
        "os_name": "unknown",
        "os_version": "unknown",
        "browser": "unknown",
        "browser_version": "unknown",
        "device": "unknown",
        "device_type": "unknown"
    }

    try:
        if request:
            user_agent_string = request.META.get('HTTP_USER_AGENT', '')
            if not user_agent_string:
                logger.warning("User-Agent não encontrado na requisição.")
                return default_info

            user_agent = parse(user_agent_string)

            client_info = {
                "os_name": user_agent.os.family or "unknown",
                "os_version": user_agent.os.version_string or "unknown",
                "browser": user_agent.browser.family or "unknown",
                "browser_version": user_agent.browser.version_string or "unknown",
                "device": user_agent.device.family or "unknown",
                "device_type": "Mobile" if user_agent.is_mobile else "Desktop"
            }

            logger.info(f"Informações do cliente obtidas: {client_info}")
            return client_info

        logger.warning("Requisição vazia ao obter informações do cliente.")
        return default_info

    except Exception as e:
        logger.error(f"Erro ao obter informações do cliente: {str(e)}")
        return default_info
