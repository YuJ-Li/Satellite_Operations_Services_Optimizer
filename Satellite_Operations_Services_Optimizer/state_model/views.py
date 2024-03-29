from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.urls import reverse
from .models import Satellite, ImageTask, MaintenanceTask, GroundStation, GroundStationRequest, Outage,SatelliteTask
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from .serializers import *
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .scheduling_algorithm import *
from .repositories import *

#test restAPI-----------------------------------------
@api_view(['GET'])
def getData(request):
    person = {'name':'kai','age':28}
    return Response(person)

# get global time
@api_view(['POST'])
def getGlobalTime(request):
    global_time = request.data['time']
            
    # SCHEDULE TASKS
    set_global_time(global_time)
    satellites = get_all_satellites()
    print(f'Got {len(satellites)} satellites')
    set_satellites(satellites)

    # maintenance tasks
    imaging_tasks = get_all_imageTask()
    print(f'Got {len(imaging_tasks)} imaging tasks')
    maintenance_tasks = get_all_maintenanceTask()
    print(f'Got {len(maintenance_tasks)} maintenance tasks')
    task_groups = associate_maintenance_tasks(maintenance_tasks)
    all_tasks = list(maintenance_tasks) + list(imaging_tasks)
    # for task_group in task_groups:
    add_new_maintenance_task(satellites, task_groups, all_tasks)

    # imaging tasks
    imaging_tasks_prio = group_by_priority(imaging_tasks)
    add_new_imaging_task(satellites,imaging_tasks_prio,imaging_tasks)
    # for prio in imaging_tasks_prio:
    #     for imaging_task in imaging_tasks_prio[prio]:
    #         add_new_imaging_task(satellites,imaging_task,imaging_tasks)
    
    for s in satellites:
        s.save()

    total=0
    for satellite in satellites:
        print(f"------{satellite.name} capacity: {satellite.capacity_used}/{satellite.storage_capacity}------")
        schedule = json.loads(satellite.schedule)
        total += len(schedule)
        for t in schedule:
            print(f"{t[0]}         {t[1]} --> {t[2]}")
    print(f'{total} imaging tasks got scheduled.')

    return Response(global_time)
    


#satellite restAPI-----------------------------------------
@api_view(['GET', 'POST'])
def satellite_list(request):
    if request.method == 'GET':
        satellites = Satellite.objects.all()
        serializer = SatelliteSerializer(satellites, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # print(f'the satellite received is {request.data}')
        name = request.data['name']
        tle = request.data['tle']
        storage_capacity = request.data['storage_capacity']
        try:
            new_satellite = add_satellite(name, tle, storage_capacity)
            all_imaging_tasks = get_all_imageTask()
            for imaging_task in all_imaging_tasks:
                achis = json.loads(imaging_task.achievability)
                achis[name] = find_satellite_achievabilities(new_satellite, imaging_task)
                imaging_task.achievability = json.dumps(achis)
                imaging_task.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # serializer = SatelliteSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def satellite_detail(request, satellite_id):
    try:
        satellite = Satellite.objects.get(name=satellite_id)

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
    

#imaging task restAPI-----------------------------------------
@api_view(['GET', 'POST'])
def imaging_task_list(request):
    if request.method == 'GET':
        tasks = ImageTask.objects.all()
        serializer = ImageTaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # GET ALL SATELLITES
        satellites = get_all_satellites()

        # PARSE AND ADD MAINTENANCE TASKS TO DATABASE
        data = request.data
        json_content = json.loads(data['jsonData'])
        name = data['name']
        imaging_tasks = convert_json_to_imaging_task(json_content, name, satellites)

        for imaging_task in imaging_tasks:
            try:
                add_imageTask(name = imaging_task.name,
                        start_time = imaging_task.start_time,
                        end_time = imaging_task.end_time,
                        priority = imaging_task.priority,
                        duration = imaging_task.duration,
                        image_type=imaging_task.image_type,
                        imagingRegionLatitude=imaging_task.imagingRegionLatitude,
                        imagingRegionLongitude=imaging_task.imagingRegionLongitude,
                        achievability=imaging_task.achievability,
                        )
                return Response(status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
    
@api_view(['GET', 'PUT', 'DELETE'])
def imaging_task_detail(request, task_id):
    try:
        task = ImageTask.objects.get(name=task_id)

        # For GET requests
        if request.method == 'GET':
            serializer = ImageTaskSerializer(task)
            return JsonResponse(serializer.data)

        # For PUT requests
        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = ImageTaskSerializer(task, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        # For DELETE requests
        elif request.method == 'DELETE':
            task.delete()
            return HttpResponse(status=204)

    except ImageTask.DoesNotExist:
        raise Http404("imagetask not found")


#MaintenanceTask restAPI-----------------------------------------
@api_view(['GET', 'POST'])
def maintenance_task_list(request):
    if request.method == 'GET':
        tasks = MaintenanceTask.objects.all()
        serializer = MaintenanceTaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # GET ALL SATELLITES
        satellites = get_all_satellites()

        # PARSE MAINTENANCE TASKS
        data = request.data
        json_content = json.loads(data['jsonData'])
        name = data['name']
        maintenance_tasks = convert_json_to_maintenance_task(json_content, name, satellites)
        for maintenance_task in maintenance_tasks:
            try:
                add_maintenanceTask(name = maintenance_task.name,
                                start_time = maintenance_task.start_time, 
                                end_time = maintenance_task.end_time, 
                                priority = maintenance_task.priority, 
                                duration = maintenance_task.duration, 
                                next_maintenance = maintenance_task.next_maintenance, 
                                # next_maintenance = '',
                                is_head = maintenance_task.is_head, 
                                min_gap = maintenance_task.min_gap, 
                                max_gap = maintenance_task.max_gap, 
                                payload_outage = maintenance_task.payload_outage,
                                satellite = maintenance_task.satellite,
                                # satellite = None
                                )
            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)
            
    
@api_view(['GET', 'PUT', 'DELETE'])
def maintenance_task_detail(request, task_id):
    try:
        task = MaintenanceTask.objects.get(name=task_id)

        # For GET requests
        if request.method == 'GET':
            serializer = MaintenanceTaskSerializer(task)
            return JsonResponse(serializer.data)

        # For PUT requests
        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = MaintenanceTaskSerializer(task, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        # For DELETE requests
        elif request.method == 'DELETE':
            task.delete()
            return HttpResponse(status=204)

    except MaintenanceTask.DoesNotExist:
        raise Http404("downlink task not found")
    
#ground satation restAPI-----------------------------------------
@api_view(['GET', 'POST'])
def ground_station_list(request):
    if request.method == 'GET':
        groundStations = GroundStation.objects.all()
        serializer = GroundStationSerializer(groundStations, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = GroundStationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def ground_station_detail(request, station_id):
    try:
        groundStation = GroundStation.objects.get(groundStationId = station_id)

        # For GET requests
        if request.method == 'GET':
            serializer = GroundStationSerializer(groundStation)
            return JsonResponse(serializer.data)

        # For PUT requests
        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = GroundStationSerializer(groundStation, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        # For DELETE requests
        elif request.method == 'DELETE':
            groundStation.delete()
            return HttpResponse(status=204)

    except GroundStation.DoesNotExist:
        raise Http404("groundstation not found")
    
#ground satation request restAPI-----------------------------------------
@api_view(['GET', 'POST'])
def ground_station_request_list(request):
    if request.method == 'GET':
        groundStationRequests = GroundStationRequest.objects.all()
        serializer = GroundStationRequestSerializer(groundStationRequests, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = GroundStationRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def ground_station_request_detail(request, stationRequest_id):
    try:
        groundStationRequest = GroundStationRequest.objects.get(requestId = stationRequest_id)

        # For GET requests
        if request.method == 'GET':
            serializer = GroundStationRequestSerializer(groundStationRequest)
            return JsonResponse(serializer.data)

        # For PUT requests
        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = GroundStationRequestSerializer(groundStationRequest, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        # For DELETE requests
        elif request.method == 'DELETE':
            groundStationRequest.delete()
            return HttpResponse(status=204)

    except GroundStationRequest.DoesNotExist:
        raise Http404("groundstationRequest not found")
    

    
#outage restAPI-----------------------------------------
@api_view(['GET', 'POST'])
def outage_list(request):
    if request.method == 'GET':
        outages = Outage.objects.all()
        serializer = OutageSerializer(outages, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':

        station_id = request.data.get('groundStation')
        if not GroundStation.objects.filter(id=station_id).exists():
            return JsonResponse({'error': 'groundstation not found'}, status=400)
        satellite_id = request.data.get('satellite')
        if not Satellite.objects.filter(id=satellite_id).exists():
            return JsonResponse({'error': 'satellite not found'}, status=400)

        serializer = OutageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def outage_detail(request, outage_id):
    try:
        outage = Outage.objects.get(outageId = outage_id)

        # For GET requests
        if request.method == 'GET':
            serializer = OutageSerializer(outage)
            return JsonResponse(serializer.data)

        # For PUT requests
        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = OutageSerializer(Outage, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        # For DELETE requests
        elif request.method == 'DELETE':
            outage.delete()
            return HttpResponse(status=204)

    except Outage.DoesNotExist:
        raise Http404("outage not found")