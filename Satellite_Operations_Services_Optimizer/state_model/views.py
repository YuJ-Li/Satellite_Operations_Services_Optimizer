from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Satellite, SatelliteSchedule
from django.utils import timezone


#satellite controller--------------------
def add_satellite(satelliteId, TLE, storageCapacity, powerCapacity, fieldOfView):
    new_satellite = Satellite(satelliteId=satelliteId,
                              TLE=TLE,
                              storageCapacity=storageCapacity,
                              powerCapacity=powerCapacity,
                              fieldOfView=fieldOfView)
    new_satellite.save()
    return new_satellite

def get_all_satellites():
    return Satellite.objects.all()

def get_satellite_by_id(satellite_id) -> Satellite:
    satellite = Satellite.objects.get(satelliteId=satellite_id)
    return satellite
def update_satellite_info(satellite_id,TLE, storageCapacity, powerCapacity, fieldOfView,satelliteSchedule):
    satellite = Satellite.objects.get(satelliteId=satellite_id)
    satellite.satelliteId = satellite.satelliteId
    satellite.TLE = TLE
    satellite.storageCapacity = storageCapacity
    satellite.powerCapacity = powerCapacity
    satellite.fieldOfView = fieldOfView
    satellite.satelliteSchedule = satelliteSchedule
    satellite.save()

def delete_satellite_by_id(satellite_id):
    try:
        satellite = Satellite.objects.get(satelliteId=satellite_id)
        satellite.delete()
    except Satellite.DoesNotExist:
        pass
#satelliteSchedule controller---------------
def add_SatelliteSchedule(scheduleId, activityWindow, satellite):
    satelliteSchedule = SatelliteSchedule(scheduleId = scheduleId, activityWindow = activityWindow, satellite = satellite)
    satelliteSchedule.save()
    return satelliteSchedule
 
def get_all_satelliteSchedules():
    return SatelliteSchedule.objects.all()

def get_satelliteSchedule_by_id(scheduleId)->SatelliteSchedule:
    return Satellite.objects.get(scheduleId)

def update_satelliteSchedule_info(scheduleId, activityWindow, satellite):
    satelliteSchedule = SatelliteSchedule.objects.get(scheduleId)
    satelliteSchedule.scheduleID = satelliteSchedule.scheduleID
    satelliteSchedule.activityWindow = activityWindow
    satelliteSchedule.satellite = satellite
    satellite.save()

def delete_satelliteSchedule_by_id(scheduleId):
    try:
        satelliteSchedule = SatelliteSchedule.objects.get(scheduleId)
        satelliteSchedule.delete()
    except satelliteSchedule.DoesNotExist:
        pass