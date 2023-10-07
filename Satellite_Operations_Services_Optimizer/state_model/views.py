from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Satellite, SatelliteSchedule
from django.utils import timezone



def add_satellite(satelliteId, TLE, storageCapacity, powerCapacity, fieldOfView):
    new_satellite = Satellite(satelliteId=satelliteId,
                              TLE=TLE,
                              storageCapacity=storageCapacity,
                              powerCapacity=powerCapacity,
                              fieldOfView=fieldOfView)
    new_satellite.save()


def get_satellite_by_id(satellite_id) -> Satellite:
    satellite = Satellite.objects.get(satelliteId=satellite_id)
    return satellite

