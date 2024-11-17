from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Device, Equipment, Maintenance
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Device)
def device_update_handler(sender, instance, created, **kwargs):
    """
    Handler para logs ao criar ou atualizar um Device.
    """
    if created:
        logger.info(f"Novo device criado: {instance.device_id}")
    else:
        logger.info(f"Device {instance.device_id} atualizado.")
    # Chama a função para atualizar as horas do equipamento e das manutenções relacionadas
    update_equipment_calculations(instance)
    update_maintenance_hours(instance)


def update_equipment_calculations(device_instance):
    """
    Atualiza o campo worked_hours para o equipamento relacionado
    sempre que o horímetro do dispositivo é atualizado.
    """
    try:
        # Tenta obter o equipamento relacionado ao dispositivo
        equipment = Equipment.objects.get(device=device_instance)
        
        # Recalcula worked_hours para o equipamento baseado no incremento do horímetro
        equipment.worked_hours = equipment.get_worked_hours()
        equipment.save()

        logger.info(f"Equipment '{equipment.name}' updated with worked_hours: {equipment.worked_hours}")

    except Equipment.DoesNotExist:
        logger.warning(f"Equipment related to device '{device_instance.device_id}' not found.")
    except Exception as e:
        logger.error(f"Error updating worked_hours for device {device_instance.device_id}: {str(e)}")


def update_maintenance_hours(device_instance):
    """
    Atualiza worked_hours e remaining_hours para cada manutenção associada ao equipamento.
    """
    try:
        # Obtém o equipamento relacionado ao dispositivo atualizado
        equipment = Equipment.objects.get(device=device_instance)
        
        # Itera sobre as manutenções relacionadas para recalcular as horas
        for maintenance in Maintenance.objects.filter(equipment=equipment):
            # Atualiza worked_hours e remaining_hours para cada manutenção
            maintenance.worked_hours = maintenance.get_worked_hours()
            maintenance.remaining_hours = maintenance.get_remaining_hours()
            maintenance.save()

            # Log para verificar as atualizações
            logger.info(f"Atualizado '{maintenance.name}' com worked_hours: {maintenance.worked_hours} e remaining_hours: {maintenance.remaining_hours}")

    except Equipment.DoesNotExist:
        logger.warning(f"Equipamento para dispositivo '{device_instance.device_id}' não encontrado.")
    except Exception as e:
        logger.error(f"Erro ao atualizar manutenções para dispositivo {device_instance.device_id}: {str(e)}")
