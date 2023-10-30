from rest_framework import serializers
from .models import Satellite, SatelliteSchedule, ImagingTask,MaintenanceTask, DownlinkTask,GroundStation, GroundStationRequest, Image, Outage, SatelliteTask

class SatelliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Satellite
        fields = '_all_'

class SatelliteScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SatelliteSchedule
        fields = '_all_'

class ImagingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagingTask
        fields = '_all_'

class MaintenanceTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTask
        fields = '_all_'

class DownlinkTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownlinkTask
        fields = '_all_'

class GroundStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroundStation
        fields = '_all_'

class GroundStationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroundStationRequest
        fields = '_all_'
    
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '_all_'

class OutageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outage
        fields = '_all_'