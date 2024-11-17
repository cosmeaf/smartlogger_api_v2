import platform
import distro
import logging

logger = logging.getLogger(__name__)

def get_machine_info():
    """Obtém informações detalhadas sobre a máquina e o sistema operacional."""
    try:
        system_info = {
            "os_name": platform.system() or "Desconhecido",
            "os_version": platform.release() or "Desconhecido",
            "machine": platform.machine() or "Desconhecido",
            "processor": platform.processor() or "Desconhecido"
        }

        # Detectar se é uma distribuição Linux
        if system_info["os_name"].lower() == "linux":
            system_info.update({
                "linux_distro": distro.name(pretty=True) or "Desconhecido",
                "linux_distro_version": distro.version(pretty=True) or "Desconhecido"
            })
        elif system_info["os_name"].lower() == "darwin":
            system_info["os_name"] = "MacOS"
            system_info["os_version"] = platform.mac_ver()[0] or "Desconhecido"
        else:
            system_info["os_name"] = system_info["os_name"].capitalize()

        logger.info(f"Informações da máquina obtidas: {system_info}")
        return system_info

    except Exception as e:
        logger.error(f"Erro ao obter informações da máquina: {str(e)}")
        return {
            "os_name": "Desconhecido",
            "os_version": "Desconhecido",
            "machine": "Desconhecido",
            "processor": "Desconhecido",
            "linux_distro": "Desconhecido",
            "linux_distro_version": "Desconhecido",
            "error": str(e)
        }
