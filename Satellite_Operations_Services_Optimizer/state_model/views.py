from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.urls import reverse
from .models import Satellite, SatelliteSchedule, ImagingTask,MaintenanceTask, DownlinkTask,GroundStation, GroundStationRequest, Image, Outage, SatelliteTask
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from .serializers import SatelliteSerializer, SatelliteScheduleSerializer
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def getData(request):
    person = {'name':'kai','age':28}
    return Response(person)

@api_view(['GET', 'POST'])
def satellite_list(request):
    if request.method == 'GET':
        satellites = Satellite.objects.all()
        serializer = SatelliteSerializer(satellites, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SatelliteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def satellite_detail(request, satellite_id):
    try:
        satellite = Satellite.objects.get(satelliteId=satellite_id)

        # For GET requests
        if request.method == 'GET':
            serializer = SatelliteSerializer(satellite)
            return JsonResponse(serializer.data)

        # For PUT requests
        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = SatelliteSerializer(satellite, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)
        elif request.method == 'DELETE':
            satellite.delete()
            return HttpResponse(status=204)  # 204 No Content is typically returned for successful DELETE requests.

    except Satellite.DoesNotExist:
        raise Http404("Satellite not found")

@api_view(['GET', 'POST'])
def satellite_schedule_list(request):
    if request.method == 'GET':
        schedules = SatelliteSchedule.objects.all()
        serializer = SatelliteScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':

        satellite_id = request.data.get('satellite')
        if not Satellite.objects.filter(satelliteId=satellite_id).exists():
            return JsonResponse({'error': 'Satellite not found'}, status=400)

        serializer = SatelliteScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def satellite_schedule_detail(request, schedule_id):
    try:
        schedule = SatelliteSchedule.objects.get(scheduleID=schedule_id)

        # For GET requests
        if request.method == 'GET':
            serializer = SatelliteScheduleSerializer(schedule)
            return JsonResponse(serializer.data)

        # For PUT requests
        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = SatelliteScheduleSerializer(schedule, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        # For DELETE requests
        elif request.method == 'DELETE':
            schedule.delete()
            return HttpResponse(status=204)

    except SatelliteSchedule.DoesNotExist:
        raise Http404("Schedule not found")