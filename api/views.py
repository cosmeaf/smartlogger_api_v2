# api/views.py
from decimal import Decimal
from rest_framework.decorators import action
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from .models import Device, Equipment, Maintenance, MaintenanceResetLog, Employee
from .serializers import (DeviceSerializer, EquipmentSerializer, MaintenanceSerializer, 
                          MaintenanceResetLogSerializer, EmployeeSerializer)

import logging

logger = logging.getLogger(__name__)

class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
class DeviceViewSet(mixins.ListModelMixin, 
                    mixins.RetrieveModelMixin, 
                    viewsets.GenericViewSet):
    """
    ViewSet apenas para leitura. Permite listar e recuperar detalhes dos dispositivos.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def get_queryset(self):
        available = self.request.query_params.get('available', None)
        if available == 'true':
            return Device.objects.filter(equipments__isnull=True)
        return Device.objects.all()



class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().order_by('id')
    serializer_class = EquipmentSerializer


class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer

    @action(detail=True, methods=['post'])
    def reset_hours(self, request, pk=None):
        instance = self.get_object()
        
        MaintenanceResetLog.objects.create(
            maintenance=instance,
            equipment_worked_hours=instance.equipment.worked_hours,
            maintenance_worked_hours=instance.worked_hours
        )
        
        instance.initial_hour_suntech = instance.equipment.device.horimeter
        instance.initial_hour_maintenance = 0
        instance.worked_hours = 0
        instance.save(update_fields=['initial_hour_suntech', 'initial_hour_maintenance', 'worked_hours'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MaintenanceResetLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaintenanceResetLog.objects.all()
    serializer_class = MaintenanceResetLogSerializer