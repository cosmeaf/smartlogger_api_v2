from django.db import models
from datetime import date
from decimal import Decimal
from model_utils import FieldTracker
import os
import uuid
import logging

logger = logging.getLogger(__name__)

def current_year():
    return date.today().year

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profile_pictures', filename)


class Device(models.Model):
    device_id = models.CharField(max_length=255, primary_key=True, unique=True)
    in_manutenance = models.BooleanField(default=False)
    hdr = models.CharField(max_length=255, verbose_name="Header", null=True, blank=True)
    report_map = models.CharField(max_length=255, verbose_name="Report Map", null=True, blank=True)
    model = models.CharField(max_length=255, verbose_name="Model", null=True, blank=True)
    software_version = models.CharField(max_length=50, verbose_name="Software Version", null=True, blank=True)
    message_type = models.CharField(max_length=50, verbose_name="Message Type", null=True, blank=True)
    date = models.DateField(verbose_name="Date", default=date.today, null=True, blank=True)
    time = models.TimeField(verbose_name="Time", null=True, blank=True)
    latitude = models.FloatField(verbose_name="Latitude", null=True, blank=True)
    longitude = models.FloatField(verbose_name="Longitude", null=True, blank=True)
    speed_gps = models.FloatField(verbose_name="Speed GPS (Km/h)", null=True, blank=True)
    course = models.CharField(max_length=50, verbose_name="Course", null=True, blank=True)
    satellites = models.IntegerField(verbose_name="Satellites", null=True, blank=True)
    gps_fix_status = models.CharField(max_length=50, verbose_name="GPS Fix Status", null=True, blank=True)
    input_state = models.CharField(max_length=255, verbose_name="Input State", null=True, blank=True)
    output_state = models.CharField(max_length=255, verbose_name="Output State", null=True, blank=True)
    mode = models.CharField(max_length=50, verbose_name="Mode", null=True, blank=True)
    report_type = models.CharField(max_length=50, verbose_name="Report Type", null=True, blank=True)
    message_number = models.CharField(max_length=50, verbose_name="Message Number", null=True, blank=True)
    reserved = models.CharField(max_length=255, verbose_name="Reserved", null=True, blank=True)
    assign_map = models.CharField(max_length=255, verbose_name="Assign Map", null=True, blank=True)
    power_voltage = models.FloatField(verbose_name="Power Voltage", null=True, blank=True)
    battery_voltage = models.FloatField(verbose_name="Battery Voltage", null=True, blank=True)
    connection_rat = models.CharField(max_length=50, verbose_name="Connection RAT", null=True, blank=True)
    acceleration_x = models.FloatField(verbose_name="Acceleration X", null=True, blank=True)
    acceleration_y = models.FloatField(verbose_name="Acceleration Y", null=True, blank=True)
    acceleration_z = models.FloatField(verbose_name="Acceleration Z", null=True, blank=True)
    adc_value = models.FloatField(verbose_name="ADC Value", null=True, blank=True)
    gps_odometer = models.FloatField(verbose_name="GPS Odometer", null=True, blank=True)
    trip_distance = models.FloatField(verbose_name="Trip Distance", null=True, blank=True)
    horimeter = models.FloatField(verbose_name="Horimeter", null=True, blank=True, default=0.0)
    trip_horimeter = models.FloatField(verbose_name="Trip Horimeter", null=True, blank=True)
    idle_time = models.FloatField(verbose_name="Idle Time", null=True, blank=True)
    impact = models.FloatField(verbose_name="Impact", null=True, blank=True)
    tracker = FieldTracker(fields=['horimeter'])
    soc_battery_voltage = models.FloatField(verbose_name="SoC (Battery Voltage)", null=True, blank=True)
    calculated_temperature = models.FloatField(verbose_name="Calculated Temperature", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")


    def __str__(self):
        return f"Device {self.device_id} - {self.model}"

    def update_hdr(self, new_hdr):
        try:
            # Se já existir algum valor em hdr
            if self.hdr:
                # Divide os valores existentes por vírgula e remove espaços extras
                existing_hdrs = [hdr.strip() for hdr in self.hdr.split(',')]
                
                # Se o novo valor não estiver na lista, o adiciona
                if new_hdr not in existing_hdrs:
                    existing_hdrs.append(new_hdr)
                    self.hdr = ','.join(existing_hdrs)
            else:
                # Se não houver valor em hdr, define diretamente o novo valor
                self.hdr = new_hdr

            # Salva as alterações no banco de dados
            self.save()

        except Exception as e:
            # Log detalhado para capturar o erro original
            logger.error(f"Failed to update HDR for device {self.device_id}. Error: {e}")
            raise ValueError(f"Failed to update HDR for device {self.device_id}. Original error: {e}") from e


class Equipment(models.Model):
    device = models.OneToOneField('Device', on_delete=models.CASCADE, related_name='equipments')
    in_manutenance = models.BooleanField(default=False, editable=False)
    initial_hour_machine = models.FloatField('Initial Hour Machine', default=0)
    initial_hour_suntech = models.FloatField('Initial Hour Suntech', default=0, editable=False)
    worked_hours = models.FloatField('Worked Hours', default=0)
    name = models.CharField('Name', max_length=255)
    model = models.CharField('Model', max_length=255, default='N/A', blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['device', 'name']),
        ]
        verbose_name_plural = "Equipment"
        verbose_name = "Equipment"

    def __str__(self):
        return f"{self.name} - {self.device.device_id}"

    def get_worked_hours(self):
        suntech_increment = self.device.horimeter - self.initial_hour_suntech
        worked_hours = self.initial_hour_machine + suntech_increment
        
        # Adicionando log para o cálculo de worked_hours
        logger.info(f"Calculating worked_hours for {self.name}: "
                    f"initial_hour_machine={self.initial_hour_machine}, "
                    f"initial_hour_suntech={self.initial_hour_suntech}, "
                    f"device_horimeter={self.device.horimeter}, "
                    f"suntech_increment={suntech_increment}, "
                    f"worked_hours={worked_hours}")
        
        return round(max(0, worked_hours), 2)

    def min_remaining_hours(self):
        """
        Retorna a menor `remaining_hours` entre as manutenções relacionadas.
        """
        return self.maintenances.aggregate(min_hours=models.Min('remaining_hours'))['min_hours']


    def save(self, *args, **kwargs):
        if self._state.adding and self.device:
            self.initial_hour_suntech = self.device.horimeter
            logger.info(f"New Equipment: setting initial_hour_suntech={self.initial_hour_suntech} for {self.name}")

        self.worked_hours = self.get_worked_hours()
        logger.info(f"Saving Equipment {self.name}: worked_hours={self.worked_hours}")

        super().save(*args, **kwargs)

        

class Maintenance(models.Model):
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE, related_name='maintenances')
    initial_hour_suntech = models.FloatField('Initial Suntech Hour', default=0)
    initial_hour_maintenance = models.FloatField('Initial Maintenance Hour', default=0)
    worked_hours = models.FloatField('Worked Hours', default=0)
    alarm_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    remaining_hours = models.FloatField('Remaining Hours', default=0)
    name = models.CharField(max_length=255)
    os = models.BooleanField(default=False)
    obs = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.equipment.name}"

    def get_worked_hours(self):
        suntech_increment = self.equipment.device.horimeter - self.initial_hour_suntech
        worked_hours = self.initial_hour_maintenance + suntech_increment
        return round(worked_hours, 2)

    def get_remaining_hours(self):
        worked_hours = self.get_worked_hours()
        remaining_hours = float(self.alarm_hours) - worked_hours
        return round(remaining_hours, 2)

    def reset_hours(self):
        self.initial_hour_suntech = self.equipment.device.horimeter
        self.initial_hour_maintenance = 0
        self.worked_hours = 0
        self.save(update_fields=['initial_hour_suntech', 'initial_hour_maintenance', 'worked_hours'])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.initial_hour_suntech = self.equipment.device.horimeter
        self.worked_hours = self.get_worked_hours()
        self.remaining_hours = self.get_remaining_hours()
        super().save(*args, **kwargs)



class MaintenanceResetLog(models.Model):
    maintenance = models.ForeignKey('Maintenance', on_delete=models.CASCADE, related_name='reset_logs')
    reset_date = models.DateTimeField(auto_now_add=True)
    equipment_worked_hours = models.FloatField('Worked Hours Equipment', default=0)
    maintenance_worked_hours = models.FloatField('Worked Hours Maintenance', default=0)
    obs = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Reset Log for {self.maintenance.name} on {self.reset_date}"
    

class Employee(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Nome")
    last_name = models.CharField(max_length=100, verbose_name="Sobrenome")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Endereço")
    position = models.CharField(max_length=100, verbose_name="Cargo", blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True, verbose_name="Data de Contratação")
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True, verbose_name="Foto de Perfil")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='employees', verbose_name="Equipamento", blank=True, null=True)  # Torna opcional

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ['last_name', 'first_name']

