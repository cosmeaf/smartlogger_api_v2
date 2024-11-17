import requests
import logging
from decouple import config

logger = logging.getLogger(__name__)

API_KEY = config('API_KEY', default=None)

def get_location_info(ip_address, timeout=5):
    """Obtém informações de localização baseadas em um endereço IP usando a API de geolocalização."""
    if not API_KEY:
        logger.error("Chave da API não configurada. Verifique o arquivo de configuração.")
        return {"error": "API key not configured"}

    try:
        logger.info(f"Tentando obter informações de localização para o IP: {ip_address}")
        response = requests.get(
            'https://api.ipgeolocation.io/ipgeo',
            params={'apiKey': API_KEY, 'ip': ip_address},
            timeout=timeout
        )
        response.raise_for_status()  # Lança uma exceção para códigos de status HTTP >= 400

        try:
            data = response.json()
        except ValueError:
            logger.error("Resposta da API não está em formato JSON.")
            return {"error": "Invalid JSON response from API"}

        location_info = {
            "ip": ip_address,
            "isp": data.get("isp", "Desconhecido"),
            "country": data.get("country_name", "Desconhecido"),
            "state": data.get("state_prov", "Desconhecido"),
            "city": data.get("city", "Desconhecido"),
            "zipcode": data.get("zipcode", "Desconhecido"),
        }

        logger.info(f"Informações de localização obtidas com sucesso: {location_info}")
        return location_info

    except requests.exceptions.Timeout:
        logger.error(f"Timeout ao tentar obter informações de geolocalização para o IP {ip_address}.")
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição para o IP {ip_address}: {str(e)}")
        return {"error": "Failed to retrieve location info"}
    except Exception as e:
        logger.error(f"Erro inesperado ao obter informações de geolocalização para o IP {ip_address}: {str(e)}")
        return {"error": "Unexpected error occurred"}
