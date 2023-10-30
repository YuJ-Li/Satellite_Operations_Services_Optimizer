from rest_framework import serializers
from .models import Satellite, SatelliteSchedule

class SatelliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Satellite
        fields = '__all__'

class SatelliteScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SatelliteSchedule
        fields = '__all__'