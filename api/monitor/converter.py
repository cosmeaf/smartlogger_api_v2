import sys
import os
import logging
import time
from django.core.wsgi import get_wsgi_application
from datetime import datetime

# Configuração do Django
sys.path.append('/root/projects/django/smartlogger_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
application = get_wsgi_application()

# Importa o modelo Device
from api.models import Device

log_dir = '/var/log'
log_file_path = os.path.join(log_dir, 'converter.log')

try:
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Starting converter script.")
except Exception as e:
    print(f"Failed to start logging: {e}")

# Caminho para o arquivo de log local
log_file_path = '/opt/traccar/logs/tracker-server.log'

# Função para calcular o SoC
def calcular_soc(tensao, V_cheio=4.2, V_vazio=3.0):
    if tensao is None:
        return None
    if tensao >= V_cheio:
        return 100
    elif tensao >= V_cheio - 0.2 * (V_cheio - V_vazio):
        return 75
    elif tensao >= V_cheio - 0.5 * (V_cheio - V_vazio):
        return 50
    elif tensao >= V_cheio - 0.8 * (V_cheio - V_vazio):
        return 25
    else:
        return 0

def calcular_y(ADC):
    if ADC is None:
        return None
    ADC = float(ADC)
    y = (0.1856 * ADC**6 
         - 4.8729 * ADC**5 
         + 51.867 * ADC**4 
         - 285.27 * ADC**3 
         + 853.52 * ADC**2 
         - 1305 * ADC 
         + 793.79)
    return round(y, 2)

# Função para converter a data
def converter_data(data_str):
    return datetime.strptime(data_str, '%Y%m%d').date()

# Função para converter strings vazias em None ou valores numéricos
def safe_float(value):
    try:
        return float(value) if value else None
    except ValueError:
        return None

def safe_int(value):
    try:
        return int(value) if value else None
    except ValueError:
        return None

# Inicializa um dicionário para armazenar os dados
dados_completos = {}

logging.info("Starting converter script.")

# Abre o arquivo de log para leitura
with open(log_file_path, 'r') as file:
    # Move o cursor do arquivo para o final
    file.seek(0, 2)
    
    try:
        while True:
            # Lê a próxima linha do arquivo
            linha = file.readline()
            if not linha:
                time.sleep(0.1)  # Aguarda um curto período antes de tentar novamente
                continue
            
            # Remove espaços extras e caracteres de nova linha
            linha = linha.strip()
            
            # Verifica se a linha contém o prefixo desejado
            if ']' in linha:
                # Parte após o ']'
                parte = linha.split(']', 1)[1].strip()
                
                # Substitui as sequências de controle literais por espaços vazios
                parte = parte.replace('\\r', '').replace('\\n', '')
                
                # Verifica se a parte restante começa com 'STT'
                if parte.startswith('STT'):
                    ascii_string = parte  # Define a variável ascii_string

                    # Processamento dos dados para 'STT'
                    if ascii_string.startswith('STT'):
                        dados = ascii_string.split(";")
                        
                        # Preenche os dados no dicionário
                        dados_completos['hdr'] = dados[0] if len(dados) > 0 else None
                        dados_completos['device_id'] = dados[1] if len(dados) > 1 else None
                        dados_completos['report_map'] = dados[2] if len(dados) > 2 else None
                        dados_completos['model'] = dados[3] if len(dados) > 3 else None
                        dados_completos['software_version'] = dados[4] if len(dados) > 4 else None
                        dados_completos['message_type'] = dados[5] if len(dados) > 5 else None
                        
                        # Converte a data para o formato correto
                        dados_completos['date'] = converter_data(dados[6]) if len(dados) > 6 else None
                        
                        dados_completos['time'] = dados[7] if len(dados) > 7 else None
                        dados_completos['latitude'] = safe_float(dados[8]) if len(dados) > 8 and dados[8] else None
                        dados_completos['longitude'] = safe_float(dados[9]) if len(dados) > 9 and dados[9] else None
                        dados_completos['speed_gps'] = safe_float(dados[10]) if len(dados) > 10 and dados[10] else None
                        dados_completos['course'] = dados[11] if len(dados) > 11 else None
                        dados_completos['satellites'] = safe_int(dados[12]) if len(dados) > 12 and dados[12] else None
                        dados_completos['gps_fix_status'] = dados[13] if len(dados) > 13 else None
                        dados_completos['input_state'] = dados[14] if len(dados) > 14 else None
                        dados_completos['output_state'] = dados[15] if len(dados) > 15 else None
                        
                        # Campos específicos do protocolo STT
                        dados_completos['mode'] = dados[16] if len(dados) > 16 else None
                        dados_completos['report_type'] = dados[17] if len(dados) > 17 else None
                        dados_completos['message_number'] = dados[18] if len(dados) > 18 else None
                        dados_completos['reserved'] = dados[19] if len(dados) > 19 else None
                        dados_completos['assign_map'] = dados[20] if len(dados) > 20 else None
                        dados_completos['power_voltage'] = safe_float(dados[21]) if len(dados) > 21 and dados[21] else None
                        dados_completos['battery_voltage'] = safe_float(dados[22]) if len(dados) > 22 and dados[22] else None
                        dados_completos['connection_rat'] = dados[23] if len(dados) > 23 else None
                        dados_completos['acceleration_x'] = safe_float(round((float(dados[24]) / 256) ** 2, 2)) if len(dados) > 24 and dados[24] else None
                        dados_completos['acceleration_y'] = safe_float(round((float(dados[25]) / 256) ** 2, 2)) if len(dados) > 25 and dados[25] else None
                        dados_completos['acceleration_z'] = safe_float(round((float(dados[26]) / 256) ** 2, 2)) if len(dados) > 26 and dados[26] else None
                        dados_completos['adc_value'] = safe_float(dados[27]) if len(dados) > 27 and dados[27] else None
                        dados_completos['gps_odometer'] = safe_float(dados[28]) if len(dados) > 28 and dados[28] else None
                        dados_completos['trip_distance'] = safe_float(dados[29]) if len(dados) > 29 and dados[29] else None
                        # Preserve o valor anterior de horimeter se o novo valor for vazio
                        dados_completos['horimeter'] = safe_float(round(float(dados[30]) / 60, 2)) if len(dados) > 30 and dados[30] else None
                        # Preserve o valor anterior de trip_horimeter se o novo valor for vazio
                        dados_completos['trip_horimeter'] = safe_float(round(float(dados[31]) / 60, 2)) if len(dados) > 31 and dados[31] else None
                        # Preserve o valor anterior de idle_time se o novo valor for vazio
                        dados_completos['idle_time'] = safe_float(round(float(dados[32]) / 60, 2)) if len(dados) > 32 and dados[32] else None
                        
                        # Evita erro ao calcular impacto se os valores forem None
                        acceleration_x = dados_completos.get('acceleration_x', 0) or 0
                        acceleration_y = dados_completos.get('acceleration_y', 0) or 0
                        acceleration_z = dados_completos.get('acceleration_z', 0) or 0
                        
                        dados_completos['impact'] = safe_float(round((acceleration_x + 
                                                                     acceleration_y + 
                                                                     acceleration_z) ** 0.5, 2))
                        dados_completos['soc_battery_voltage'] = calcular_soc(dados_completos.get('power_voltage', None))
                        dados_completos['calculated_temperature'] = calcular_y(dados_completos.get('adc_value', None))

                    # Obtenha ou crie o dispositivo, preservando valores anteriores se os novos valores forem None
                    device, created = Device.objects.get_or_create(device_id=dados_completos['device_id'])

                    # Atualizar o campo 'hdr' sem sobrescrever valores existentes
                    device.update_hdr(dados_completos['hdr'])

                    # Atualizar os demais campos do dispositivo, mantendo os valores anteriores se os novos forem None
                    for key, value in dados_completos.items():
                        if key != 'hdr' and value is not None:  # hdr já foi tratado e não atualiza com None
                            setattr(device, key, value if value is not None else getattr(device, key))

                    device.save()

                    if created:
                        logging.info(f"New device created: {device.device_id}")
                    else:
                        logging.info(f"Device updated: {device.device_id}")

    except KeyboardInterrupt:
        logging.info("Converter script interrupted by user.")
        print("Execução interrompida pelo usuário.")