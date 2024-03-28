from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Satellite, ImageTask, MaintenanceTask, GroundStation, GroundStationRequest, Outage, SatelliteTask
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from .scheduling_algorithm import *
# from .edf_priority import *
from .satellite_service import *
from datetime import timedelta
from django.db import transaction
import json

#satellite controller--------------------
def add_satellite(satelliteId, tle, storage_capacity):
    try:
        new_satellite = Satellite(name=satelliteId, 
                                  schedule=json.dumps([]), 
                                  maintenance_without_outage=json.dumps([]),
                                  tle=tle,
                                  storage_capacity=storage_capacity,
                                  capacity_used = 0.0
                                  )
        new_satellite.save()
        return new_satellite
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_all_satellites():
    try:
        return Satellite.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_satellite_by_id(satellite_id) -> Satellite:
    try:
        satellite = Satellite.objects.get(satelliteId=satellite_id)
        return satellite
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('satellite not found.')

def update_satellite_info(satellite_id,TLE, storageCapacity, powerCapacity, fieldOfView):
    try:
        satellite = Satellite.objects.get(satelliteId=satellite_id)
        satellite.satelliteId = satellite.satelliteId
        satellite.TLE = TLE
        satellite.storageCapacity = storageCapacity
        satellite.powerCapacity = powerCapacity
        satellite.fieldOfView = fieldOfView
        # satellite.satelliteSchedule = satelliteSchedule
        satellite.save()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('Satellite not found.')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def delete_satellite_by_id(satellite_id):
    try:
        satellite = Satellite.objects.get(satelliteId=satellite_id)
        satellite.delete()
    except Satellite.DoesNotExist:
        return HttpResponseBadRequest('Satellite not found.')

# #satelliteSchedule controller---------------
# def add_SatelliteSchedule(scheduleId, activityWindowStart,activityWindowEnd, satellite):
#     try:
#         satelliteSchedule = SatelliteSchedule(scheduleID = scheduleId, activityWindowStart = activityWindowStart,activityWindowEnd = activityWindowEnd, satellite = satellite)
#         satelliteSchedule.save()
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
 
# def get_all_satelliteSchedules():
#     try:
#         return SatelliteSchedule.objects.all()
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# def get_satelliteSchedule_by_id(scheduleId)->SatelliteSchedule:
#     try:
#         return SatelliteSchedule.objects.get(scheduleID  = scheduleId)
#     except SatelliteSchedule.DoesNotExist:
#         return HttpResponseBadRequest('SatelliteSchedule not found.')

# def update_satelliteSchedule_info(scheduleId, activityWindowStart,activityWindowEnd, satellite):
#     try:
#         satelliteSchedule = SatelliteSchedule.objects.get(scheduleID=scheduleId)
#         satelliteSchedule.scheduleID = satelliteSchedule.scheduleID
#         satelliteSchedule.activityWindowStart = activityWindowStart
#         satelliteSchedule.satellite = satellite
#         satelliteSchedule.activityWindowEnd = activityWindowEnd
#         satelliteSchedule.save()
#     except SatelliteSchedule.DoesNotExist:
#         return HttpResponseBadRequest('SatelliteSchedule not found.')
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# def delete_satelliteSchedule_by_id(scheduleId):
#     try:
#         satelliteSchedule = SatelliteSchedule.objects.get(scheduleID = scheduleId)
#         satelliteSchedule.delete()
#     except satelliteSchedule.DoesNotExist:
#         pass

#imageTask controller--------------------
# def add_imageTask(name, start_time, end_time, priority, duration, image_type, imagingRegionLatitude, imagingRegionLongitude):
#     try:
#         imagingTask = ImageTask(
#             name = name, 
#             start_time = start_time,
#             end_time = end_time, 
#             priority = priority,
#             duration = duration,
#             # image_type = image_type,
#             imagingRegionLatitude = imagingRegionLatitude,
#             imagingRegionLongitude = imagingRegionLongitude,
#             # satellite = satellite
#         )
#         imagingTask.save()
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
    
def add_imageTask(name, priority, start_time, end_time, duration, image_type, imagingRegionLatitude, imagingRegionLongitude, achievability):
    try:
        imagingTask = ImageTask(
            name = name, 
            start_time = start_time,
            end_time = end_time, 
            priority = priority,
            duration = duration,
            image_type = image_type,
            imagingRegionLatitude = imagingRegionLatitude,
            imagingRegionLongitude = imagingRegionLongitude,
            achievability = achievability,
        )
        imagingTask.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def get_all_imageTask():
    try:
        return ImageTask.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_imageTask_by_id(TaskID)->ImageTask:
    try:
        it = ImageTask.objects.get(TaskID = TaskID)
        return it
    except ImageTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')
    
def updata_imageTask_info(TaskID, revisitFrequency, priority,imagingRegionLatitude,
                    imagingRegionLongitude,imagingTime,deliveryTime,schedule,startTime,endTime,duration):
    try:
        it = ImageTask.objects.get(TaskID = TaskID)
        it.revisitFrequency = revisitFrequency
        it.priority = priority
        it.startTime = startTime
        it.endTime = endTime
        it.duration = duration
        it.imagingRegionLatitude = imagingRegionLatitude
        it.imagingRegionLongitude = imagingRegionLongitude
        it.imagingTime = imagingTime
        it.deliveryTime = deliveryTime
        it.schedule = schedule
        it.save()
    except ImageTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def delete_imageTask_by_id(TaskID):
    try:
        it = ImageTask.objects.get(TaskID = TaskID)
        it.delete()
    except ImageTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')
    
#MaintenanceTask controller--------------------
def add_maintenanceTask(name, start_time, end_time, priority, duration, next_maintenance, is_head, min_gap, max_gap, payload_outage, satellite):
    try:
        maintenanceTask = MaintenanceTask(
            name = name, 
            start_time = start_time, 
            end_time = end_time, 
            priority = priority, 
            duration = duration, 
            next_maintenance = next_maintenance,
            is_head = is_head, 
            min_gap = min_gap,
            max_gap = max_gap, 
            payload_outage = payload_outage, 
            satellite = satellite, 
        )
        maintenanceTask.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_maintenanceTask():
    try:
        return MaintenanceTask.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_maintenanceTask_by_id(TaskID)->MaintenanceTask:
    try:
        it = MaintenanceTask.objects.get(TaskID = TaskID)
        return it
    except MaintenanceTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')
    
def updata_maintenanceTask_info(TaskID, revisitFrequency, priority,target,timeWindow,duration,
                        payloadOperationAffected,schedule,startTime, endTime):
    try:
        mt = MaintenanceTask.objects.get(TaskID = TaskID)
        mt.revisitFrequency = revisitFrequency
        mt.priority = priority
        mt.target = target
        mt.timeWindow = timeWindow
        mt.payloadOperationAffected = payloadOperationAffected
        mt.duration = duration
        mt.schedule = schedule
        mt.startTime = startTime
        mt.endTime = endTime
        mt.save()
    except MaintenanceTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def delete_maintenanceTask_by_id(TaskID):
    try:
        it = MaintenanceTask.objects.get(TaskID = TaskID)
        it.delete()
    except MaintenanceTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')
    
#DownlinkTask controller--------------------
# def add_downlinkTaskTask(TaskID, revisitFrequency, priority,imageId,startTime,endTime,duration,schedule):
#     try:
#         downlinkTask = DownlinkTask(
#             TaskID = TaskID,
#             revisitFrequency = revisitFrequency,
#             priority = priority,
#             imageId = imageId,
#             startTime = startTime,
#             endTime = endTime,
#             duration = duration,
#             schedule = schedule
#         )
#         downlinkTask.save()
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# def get_all_downlinkTask():
#     try:
#         return DownlinkTask.objects.all()
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
    
# def get_downlinkTask_by_id(TaskID)->DownlinkTask:
#     try:
#         it = DownlinkTask.objects.get(TaskID = TaskID)
#         return it
#     except DownlinkTask.DoesNotExist:
#         return HttpResponseBadRequest('task not found.')
    
# def update_downlinkTask_info(TaskID, revisitFrequency, priority,imageId,schedule,startTime,endTime,duration):
#     try:
#         dt = DownlinkTask.objects.get(TaskID = TaskID)
#         dt.revisitFrequency = revisitFrequency
#         dt.priority = priority
#         dt.imageId=imageId
#         dt.schedule = schedule
#         dt.startTime = startTime
#         dt.endTime = endTime
#         dt.duration
#         dt.save()
#     except DownlinkTask.DoesNotExist:
#         return HttpResponseBadRequest('task not found.')    
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
    
# def delete_downlinkTask_by_id(TaskID):
#     try:
#         it = DownlinkTask.objects.get(TaskID = TaskID)
#         it.delete()
#     except DownlinkTask.DoesNotExist:
#         return HttpResponseBadRequest('task not found.')


#groundStation controller--------------------
def add_groundStation(groundStationId, stationName, latitude,longitude ,height,stationMask,uplinkRate,downlinkRate):
    try:
        new_groundStation = GroundStation(groundStationId=groundStationId,
                                stationName=stationName,
                                latitude =latitude,
                                longitude=longitude,
                                height=height,
                                stationMask=stationMask,
                                uplinkRate = uplinkRate,
                                downlinkRate = downlinkRate)
        new_groundStation.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_groundStations():
    try:
        return GroundStation.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_groundStation_by_id(groundStationId) -> GroundStation:
    try:
        groundStation = GroundStation.objects.get(groundStationId =groundStationId)
        return groundStation
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('groundStation not found.')

def update_groundStation_info(groundStationId, stationName, latitude,longitude ,height,stationMask,uplinkRate,downlinkRate):
    try:
        groundStation = GroundStation.objects.get(groundStationId =groundStationId)
        groundStation.groundStationId =groundStationId
        groundStation.stationName = stationName
        groundStation.latitude = latitude
        groundStation.longitude = longitude
        groundStation.height = height
        groundStation.stationMask = stationMask
        groundStation.uplinkRate = uplinkRate
        groundStation.downlinkRate = downlinkRate
        groundStation.save()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('groundStation not found.')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def delete_groundStation_by_id(groundStationId):
    try:
        groundStation = GroundStation.objects.get(groundStationId =groundStationId)
        groundStation.delete()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('groundStation not found.')

#groundStationRequest controller--------------------
def add_groundStationRequest(requestId,acquisitionOfSignal,lossOfSignal,satelliteId,groundStation):
    try:
        new_groundStationRequest = GroundStationRequest(
            requestId = requestId,
            acquisitionOfSignal = acquisitionOfSignal,
            lossOfSignal = lossOfSignal,
            satelliteId = satelliteId,
            groundStation = groundStation
        )
        new_groundStationRequest.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_groundStationRequest():
    try:
        return GroundStationRequest.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_groundStationRequest_by_id(requestId) -> GroundStationRequest:
    try:
        request = GroundStationRequest.objects.get(requestId = requestId)
        return request
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('groundStationRequest not found.')

def update_groundStationRequest_info(requestId,acquisitionOfSignal,lossOfSignal,satelliteId,groundStation):
    try:
        groundStationRequest = GroundStationRequest.objects.get(requestId=requestId)
        groundStationRequest.acquisitionOfSignal = acquisitionOfSignal
        groundStationRequest.lossOfSignal = lossOfSignal
        groundStationRequest.satelliteId = satelliteId
        groundStationRequest.groundStation = groundStation
        groundStationRequest.save()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('groundStationRequest not found.')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def delete_groundStationRequest_by_id(requestId):
    try:
        groundStationRequest = GroundStationRequest.objects.get(requestId = requestId)
        groundStationRequest.delete()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('groundStationRequest not found.')

#image controller--------------------
# def add_image(imageId,imageSize,imageType,groundStationRequest,imagingTask):
#     try:
#         image = Image(imageId= imageId,
#                       imageSize = imageSize,
#                       imageType = imageType,
#                       groundStationRequest = groundStationRequest,
#                       imagingTask = imagingTask)
#         image.save()
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# def get_all_images():
#     try:
#         return Image.objects.all()
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# def get_image_by_id(imageId) -> Image:
#     try:
#         image = Image.objects.get(imageId=imageId)
#         return image
#     except ObjectDoesNotExist:
#         return HttpResponseBadRequest('image not found.')

# def update_image_info(imageId,imageSize,imageType,groundStationRequest,imagingTask):
#     try:
#         image = Image.objects.get(imageId=imageId)
#         image.imageSize = imageSize
#         image.imageType = imageType
#         image.groundStationRequest = groundStationRequest
#         image.imagingTask = imagingTask
#         image.save()
#     except ObjectDoesNotExist:
#         return HttpResponseBadRequest('image not found.')
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# def delete_image_by_id(imageId):
#     try:
#         image = Image.objects.get(imageId=imageId)
#         image.delete()
#     except Image.DoesNotExist:
#         return HttpResponseBadRequest('image not found.')
    
#Outage controller-------------------
def add_outage(outageId,startTime,endTime,groundStation,satellite):
    try:
        outage = Outage(outageId=outageId,
                        startTime=startTime,
                        endTime=endTime,
                        groundStation=groundStation,
                        satellite=satellite)
        outage.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_outage():
    try:
        return Outage.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_outage_by_id(outageId) -> Outage:
    try:
        outage = Outage.objects.get(outageId=outageId)
        return outage
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('outage not found.')

def update_outage_info(outageId,startTime,endTime,groundStation,satellite):
    try:
        outage = Outage.objects.get(outageId=outageId)
        outage.startTime = startTime
        outage.endTime = endTime
        outage.groundStation = groundStation
        outage.satellite = satellite
        outage.save()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('outage not found.')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def delete_outage_by_id(outageId):
    try:
        outage = Outage.objects.get(outageId=outageId)
        outage.delete()
    except Outage.DoesNotExist:
        return HttpResponseBadRequest('outage not found.')

###############controller for satellite scheduling##########################

def importTestCaseForSchedulingImagingTask(satellites_group, image_tasks_group, maintenance_tasks_group):
    # print('--------------------HELLO STAELLITE TASKS----------------------')
    satellites = initialize_satellites(satellites_group)
    imaging_tasks = initialize_imaging_tasks(image_tasks_group, satellites)
    maintenance_tasks = initialize_maintenance_tasks(maintenance_tasks_group, satellites)

    for satellite in satellites:
        add_satellite(satelliteId=satellite.name, tle=satellite.tle, storage_capacity=satellite.storage_capacity)
    
    for imaging_task in imaging_tasks:
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
    for maintenance_task in maintenance_tasks:
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
    print('IMPORT FINISHED.')

def performingAlgorithumImaginTask():
    #transfer data from DB to algorithm data
    satellites = get_all_satellites()
    print(f'Got {len(satellites)} satellites')
    set_satellites(satellites)

    # add imaging tasks
    imaging_tasks = get_all_imageTask()
    print(f'Got {len(imaging_tasks)} imaging tasks')
    imaging_tasks_prio = group_by_priority(imaging_tasks)

    set_global_time("2023-10-02 00:00:00")

    # perform edf
    for prio in imaging_tasks_prio:
        for imaging_task in imaging_tasks_prio[prio]:
            add_new_imaging_task(satellites,imaging_task)
    total=0
    for satellite in satellites:
        print(f"------{satellite.name} capacity: {satellite.capacity_used}/{satellite.storage_capacity}------")
        schedule = json.loads(satellite.schedule)
        total += len(schedule)
        for t in schedule:
            print(f"{t[0]}         {t[1]} --> {t[2]}")
    print(f'{total} imaging tasks got scheduled.')

    # add maintenance tasks
    maintenance_tasks = get_all_maintenanceTask()
    print(f'Got {len(maintenance_tasks)} maintenance tasks')
    # maintenenace_tasks_prio = group_by_priority(maintenance_tasks)

    # associate maintenance tasks with their next occurences
    task_groups = associate_maintenance_tasks(maintenance_tasks)

    set_global_time("2023-11-18 00:00:00")    

    for task_group in task_groups:
        # for maintenance_task in maintenenace_tasks_prio[prio]:
        add_new_maintenance_task(satellites, task_group)
        print('done')
        total=0
        for satellite in satellites:
            print(f"------{satellite.name} capacity: {satellite.capacity_used}/{satellite.storage_capacity}------")
            schedule = json.loads(satellite.schedule)
            total += len(schedule)
            for t in schedule:
                print(f"{t[0]}         {t[1]} --> {t[2]}")
                # print(t[0].name, t[1], t[2])
            
            maintenance_without_outage = json.loads(satellite.maintenance_without_outage)
            print("(Maintenances without payload outage: )")
            total += len(maintenance_without_outage)
            for t in maintenance_without_outage:
                print(f"{t[0]}         {t[1]} --> {t[2]}")
        print(f'{total} tasks got scheduled.')
    
    return total


####################ground station scheduling########################
def sortSatellitesByDeadlineAndTaskPriorityAndNumberOfTasks():
    #find the minimum and maxinum value of number of tasks and sum of priority
    #weight of priority is 10%, wight of number of tasks is 30%, shortest deadline 60%
    defaultDif = 0.05
    satellites = get_all_satellites()
    minPriority = float('inf')
    minNumberTasks = float('inf')
    minTimeTillNow = float('inf')
    maxPriority = 0
    maxNumberTasks = 0
    maxTimeTillNow = 0
    now = timezone.now()
    for satellite in satellites:
        priority = 0
        numberTasks = len(satellite.satelliteSchedule.downlink_tasks.all()) + len(satellite.satelliteSchedule.maintenance_tasks.all())+len(satellite.satelliteSchedule.imaging_tasks.all())
        timeTillNow = 0
        for task in satellite.satelliteSchedule.downlink_tasks.all():
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        for task in satellite.satelliteSchedule.maintenance_tasks.all():
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        for task in satellite.satelliteSchedule.imaging_tasks.all():
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        #find the min and max values
        if(priority <= minPriority):
            minPriority = priority
        if(priority >= maxPriority):
            maxPriority = priority

        if(numberTasks <= minNumberTasks):
            minNumberTasks = numberTasks
        if(numberTasks >= maxNumberTasks):
            maxNumberTasks = numberTasks
        
        if(timeTillNow <= minTimeTillNow):
            minTimeTillNow = timeTillNow
        if(timeTillNow >= minTimeTillNow):
            maxTimeTillNow = timeTillNow
    # print("minPriority: "+str(minPriority))
    # print("maxPriority: "+str(maxPriority))
    # print("minNumberTasks: "+str(minNumberTasks))
    # print("minNumberTasks: "+str(maxNumberTasks))
    # print("minTimeTillNow: "+str(minTimeTillNow))
    # print("maxTimeTillNow: "+str(maxTimeTillNow))
    #normalize each variables and weight them with ratio
    satelliteDic = {}
    for satellite in satellites:
        priority = 0
        numberTasks = len(satellite.satelliteSchedule.downlink_tasks.all()) + len(satellite.satelliteSchedule.maintenance_tasks.all())+len(satellite.satelliteSchedule.imaging_tasks.all())
        timeTillNow = 0
        for task in satellite.satelliteSchedule.downlink_tasks.all():
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        for task in satellite.satelliteSchedule.maintenance_tasks.all():
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        for task in satellite.satelliteSchedule.imaging_tasks.all():
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        # print("Priority: "+str(priority))
        # print("NumberTasks: "+str(numberTasks))
        # print("TimeTillNow: "+str(timeTillNow))
        satelliteDic[satellite] = (0.1*(priority - minPriority)/(maxPriority - minPriority+defaultDif)) + (0.3 * ((numberTasks - minNumberTasks)/(maxNumberTasks - minNumberTasks+defaultDif))) + (-0.6* ((timeTillNow - minTimeTillNow)/(maxTimeTillNow - minTimeTillNow+defaultDif)))
    #sort satellite by the values
    # print("before sort")
    # print(satelliteDic)
    #print dic for debugging
    sorted_satellites = sorted(satelliteDic.items(), key=lambda item: item[1], reverse=True)
    #return the sorted satellite
    print("after sort")
    print(sorted_satellites)
    return [satellite_tuple[0] for satellite_tuple in sorted_satellites]

def performGroundStationScheduling():
    groundStations = get_all_groundStations()
    satellites = sortSatellitesByDeadlineAndTaskPriorityAndNumberOfTasks()
    now = timezone.now()
    #for each satellites. find the takes place first
    satellitesDic = {}
    for satellite in satellites:
        firstDeadline = now + timedelta(days=1024)
        for task in satellite.satelliteSchedule.downlink_tasks.all():
            if (task.startTime < firstDeadline and task.startTime > now):
                firstDeadline = task.startTime
        for task in satellite.satelliteSchedule.maintenance_tasks.all():
            if (task.startTime < firstDeadline and task.startTime > now):
                firstDeadline = task.startTime
        for task in satellite.satelliteSchedule.imaging_tasks.all():
            if (task.startTime < firstDeadline and task.startTime > now):
                firstDeadline = task.startTime
        satellitesDic[satellite] = firstDeadline

    #put satellite to each ground station    
    timescale = load.timescale()
    for satellite, dl in satellitesDic.items():
        for groundStation in groundStations:
            s = define_satellite(satellite.TLE)
            g = define_groundstation(groundStation.latitude,groundStation.longitude,groundStation.height)
            startTime = timescale.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
            endTime = timescale.utc(dl.year, dl.month, dl.day, dl.hour, dl.minute, dl.second)
            timeWindows = get_time_window(s,g,startTime,endTime,satellite.fieldOfView)
            print(timeWindows)
            if(len(timeWindows)>0):
                add_groundStationRequest(requestId=(groundStation.groundStationId + "request"),acquisitionOfSignal=timeWindows[0][0],lossOfSignal=timeWindows[0][1],satelliteId = satellite.satelliteId,groundStation=groundStation)
                break
    #sort satellites by task priority
    #log the result of the scheduling
    print("###ground satation result####")
    groundStations = get_all_groundStations()
    for gs in groundStations:
        print(gs.groundStationId+" :")
        for request in gs.ground_station_requests.all():
            print(request.satellite_id)

        


