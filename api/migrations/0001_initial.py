# Generated by Django 5.1.2 on 2024-11-01 12:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('device_id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('in_manutenance', models.BooleanField(default=False)),
                ('hdr', models.CharField(blank=True, max_length=255, null=True, verbose_name='Header')),
                ('report_map', models.CharField(blank=True, max_length=255, null=True, verbose_name='Report Map')),
                ('model', models.CharField(blank=True, max_length=255, null=True, verbose_name='Model')),
                ('software_version', models.CharField(blank=True, max_length=50, null=True, verbose_name='Software Version')),
                ('message_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='Message Type')),
                ('date', models.DateField(blank=True, default=datetime.date.today, null=True, verbose_name='Date')),
                ('time', models.TimeField(blank=True, null=True, verbose_name='Time')),
                ('latitude', models.FloatField(blank=True, null=True, verbose_name='Latitude')),
                ('longitude', models.FloatField(blank=True, null=True, verbose_name='Longitude')),
                ('speed_gps', models.FloatField(blank=True, null=True, verbose_name='Speed GPS (Km/h)')),
                ('course', models.CharField(blank=True, max_length=50, null=True, verbose_name='Course')),
                ('satellites', models.IntegerField(blank=True, null=True, verbose_name='Satellites')),
                ('gps_fix_status', models.CharField(blank=True, max_length=50, null=True, verbose_name='GPS Fix Status')),
                ('input_state', models.CharField(blank=True, max_length=255, null=True, verbose_name='Input State')),
                ('output_state', models.CharField(blank=True, max_length=255, null=True, verbose_name='Output State')),
                ('mode', models.CharField(blank=True, max_length=50, null=True, verbose_name='Mode')),
                ('report_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='Report Type')),
                ('message_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Message Number')),
                ('reserved', models.CharField(blank=True, max_length=255, null=True, verbose_name='Reserved')),
                ('assign_map', models.CharField(blank=True, max_length=255, null=True, verbose_name='Assign Map')),
                ('power_voltage', models.FloatField(blank=True, null=True, verbose_name='Power Voltage')),
                ('battery_voltage', models.FloatField(blank=True, null=True, verbose_name='Battery Voltage')),
                ('connection_rat', models.CharField(blank=True, max_length=50, null=True, verbose_name='Connection RAT')),
                ('acceleration_x', models.FloatField(blank=True, null=True, verbose_name='Acceleration X')),
                ('acceleration_y', models.FloatField(blank=True, null=True, verbose_name='Acceleration Y')),
                ('acceleration_z', models.FloatField(blank=True, null=True, verbose_name='Acceleration Z')),
                ('adc_value', models.FloatField(blank=True, null=True, verbose_name='ADC Value')),
                ('gps_odometer', models.FloatField(blank=True, null=True, verbose_name='GPS Odometer')),
                ('trip_distance', models.FloatField(blank=True, null=True, verbose_name='Trip Distance')),
                ('horimeter', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Horimeter')),
                ('trip_horimeter', models.FloatField(blank=True, null=True, verbose_name='Trip Horimeter')),
                ('idle_time', models.FloatField(blank=True, null=True, verbose_name='Idle Time')),
                ('impact', models.FloatField(blank=True, null=True, verbose_name='Impact')),
                ('soc_battery_voltage', models.FloatField(blank=True, null=True, verbose_name='SoC (Battery Voltage)')),
                ('calculated_temperature', models.FloatField(blank=True, null=True, verbose_name='Calculated Temperature')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última Atualização')),
            ],
        ),
    ]
