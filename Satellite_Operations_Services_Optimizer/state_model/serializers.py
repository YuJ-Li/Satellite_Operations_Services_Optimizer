from rest_framework import serializers
from .models import *

class SatelliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Satellite
        fields = '__all__'

# class SatelliteScheduleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SatelliteSchedule
#         fields = '__all__'

class MaintenanceTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTask
        fields = '__all__'

# class DownlinkTaskSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DownlinkTask
#         fields = '__all__'

class GroundStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroundStation
        fields = '__all__'

class GroundStationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroundStationRequest
        fields = '__all__'

# class ImageTypeSerializer():
#     class Meta:
#         model = ImageType
#         fields = '__all__' 

class ImageTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageTask
        fields = '__all__' 

# class ImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Image
#         fields = '__all__'

class OutageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outage
        fields = '__all__'