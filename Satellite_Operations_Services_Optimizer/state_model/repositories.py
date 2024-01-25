from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Satellite, SatelliteSchedule, ImagingTask,MaintenanceTask, DownlinkTask,GroundStation, GroundStationRequest, Image, Outage, SatelliteTask
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from .scheduling_algorithm import *
from .edf_priority import *
from .satellite_service import *
from datetime import timedelta
#satellite controller--------------------
def add_satellite(satelliteId, TLE, storageCapacity, powerCapacity, fieldOfView):
    try:
        new_satellite = Satellite(satelliteId=satelliteId,
                                TLE=TLE,
                                storageCapacity=storageCapacity,
                                powerCapacity=powerCapacity,
                                fieldOfView=fieldOfView)
        new_satellite.save()
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

#satelliteSchedule controller---------------
def add_SatelliteSchedule(scheduleId, activityWindowStart,activityWindowEnd, satellite):
    try:
        satelliteSchedule = SatelliteSchedule(scheduleID = scheduleId, activityWindowStart = activityWindowStart,activityWindowEnd = activityWindowEnd, satellite = satellite)
        satelliteSchedule.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 
def get_all_satelliteSchedules():
    try:
        return SatelliteSchedule.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_satelliteSchedule_by_id(scheduleId)->SatelliteSchedule:
    try:
        return SatelliteSchedule.objects.get(scheduleID  = scheduleId)
    except SatelliteSchedule.DoesNotExist:
        return HttpResponseBadRequest('SatelliteSchedule not found.')

def update_satelliteSchedule_info(scheduleId, activityWindowStart,activityWindowEnd, satellite):
    try:
        satelliteSchedule = SatelliteSchedule.objects.get(scheduleID=scheduleId)
        satelliteSchedule.scheduleID = satelliteSchedule.scheduleID
        satelliteSchedule.activityWindowStart = activityWindowStart
        satelliteSchedule.satellite = satellite
        satelliteSchedule.activityWindowEnd = activityWindowEnd
        satelliteSchedule.save()
    except SatelliteSchedule.DoesNotExist:
        return HttpResponseBadRequest('SatelliteSchedule not found.')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def delete_satelliteSchedule_by_id(scheduleId):
    try:
        satelliteSchedule = SatelliteSchedule.objects.get(scheduleID = scheduleId)
        satelliteSchedule.delete()
    except satelliteSchedule.DoesNotExist:
        pass

#imageTask controller--------------------
def add_imagingTask(TaskID, revisitFrequency, priority,imagingRegionLatitude,
                    imagingRegionLongitude,imagingTime,deliveryTime,schedule,startTime,endTime,duration):
    try:
        imagingTask = ImagingTask(
            TaskID = TaskID,
            revisitFrequency = revisitFrequency,
            priority = priority,
            startTime = startTime,
            endTime = endTime,
            duration = duration,
            imagingRegionLatitude = imagingRegionLatitude,
            imagingRegionLongitude = imagingRegionLongitude,
            imagingTime = imagingTime,
            deliveryTime = deliveryTime,
            schedule = schedule
        )
        imagingTask.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_imagingTask():
    try:
        return ImagingTask.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_imagingTask_by_id(TaskID)->ImagingTask:
    try:
        it = ImagingTask.objects.get(TaskID = TaskID)
        return it
    except ImagingTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')
    
def updata_imagingTask_info(TaskID, revisitFrequency, priority,imagingRegionLatitude,
                    imagingRegionLongitude,imagingTime,deliveryTime,schedule,startTime,endTime,duration):
    try:
        it = ImagingTask.objects.get(TaskID = TaskID)
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
    except ImagingTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def delete_imagingTask_by_id(TaskID):
    try:
        it = ImagingTask.objects.get(TaskID = TaskID)
        it.delete()
    except ImagingTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')
    
#MaintenanceTask controller--------------------
def add_maintenanceTask(TaskID, revisitFrequency, priority,target,timeWindow,duration,
                        payloadOperationAffected,schedule,startTime,endTime):
    try:
        maintenanceTask = MaintenanceTask(
            TaskID = TaskID,
            revisitFrequency = revisitFrequency,
            priority = priority,
            startTime = startTime,
            endTime = endTime,
            target = target,
            timeWindow = timeWindow,
            duration = duration,
            payloadOperationAffected = payloadOperationAffected,
            schedule = schedule
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
def add_downlinkTaskTask(TaskID, revisitFrequency, priority,imageId,startTime,endTime,duration,schedule):
    try:
        downlinkTask = DownlinkTask(
            TaskID = TaskID,
            revisitFrequency = revisitFrequency,
            priority = priority,
            imageId = imageId,
            startTime = startTime,
            endTime = endTime,
            duration = duration,
            schedule = schedule
        )
        downlinkTask.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_downlinkTask():
    try:
        return DownlinkTask.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_downlinkTask_by_id(TaskID)->DownlinkTask:
    try:
        it = DownlinkTask.objects.get(TaskID = TaskID)
        return it
    except DownlinkTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')
    
def update_downlinkTask_info(TaskID, revisitFrequency, priority,imageId,schedule,startTime,endTime,duration):
    try:
        dt = DownlinkTask.objects.get(TaskID = TaskID)
        dt.revisitFrequency = revisitFrequency
        dt.priority = priority
        dt.imageId=imageId
        dt.schedule = schedule
        dt.startTime = startTime
        dt.endTime = endTime
        dt.duration
        dt.save()
    except DownlinkTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def delete_downlinkTask_by_id(TaskID):
    try:
        it = DownlinkTask.objects.get(TaskID = TaskID)
        it.delete()
    except DownlinkTask.DoesNotExist:
        return HttpResponseBadRequest('task not found.')


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
def add_image(imageId,imageSize,imageType,groundStationRequest,imagingTask):
    try:
        image = Image(imageId= imageId,
                      imageSize = imageSize,
                      imageType = imageType,
                      groundStationRequest = groundStationRequest,
                      imagingTask = imagingTask)
        image.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_all_images():
    try:
        return Image.objects.all()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_image_by_id(imageId) -> Image:
    try:
        image = Image.objects.get(imageId=imageId)
        return image
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('image not found.')

def update_image_info(imageId,imageSize,imageType,groundStationRequest,imagingTask):
    try:
        image = Image.objects.get(imageId=imageId)
        image.imageSize = imageSize
        image.imageType = imageType
        image.groundStationRequest = groundStationRequest
        image.imagingTask = imagingTask
        image.save()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('image not found.')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def delete_image_by_id(imageId):
    try:
        image = Image.objects.get(imageId=imageId)
        image.delete()
    except Image.DoesNotExist:
        return HttpResponseBadRequest('image not found.')
    
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
def importTestCaseForSchedulingImagingTask():
    #print("#####importing the test cse for scheduling#####")
    _, satellites, _, imaging_tasks = initialize_satellites_tasks()
    for satellite in satellites:
        add_satellite(satelliteId=satellite.name,TLE=satellite.tle,storageCapacity=10,powerCapacity=10,fieldOfView=10)
        add_SatelliteSchedule(scheduleId=(satellite.name+"schedule"),activityWindowStart=satellite.activity_window[0],activityWindowEnd=satellite.activity_window[1],satellite=get_satellite_by_id(satellite.name))
    
    #default satellite to initially store tasks
    add_satellite(satelliteId="admin123",TLE="admin123",storageCapacity=0,powerCapacity=0,fieldOfView=0)
    add_SatelliteSchedule(scheduleId="admin123_schedule",activityWindowStart=datetime(2023, 1, 1, 00, 00, 00),activityWindowEnd=datetime(2023, 1, 1, 00, 00, 00),satellite=get_satellite_by_id("admin123"))
    # print("satelliteSize: ")
    # print(len(get_all_satellites()))

    i=0
    for imaging_task in imaging_tasks:
        add_imagingTask(TaskID=imaging_task.name+str(i),revisitFrequency=1,priority=imaging_task.priority,imagingRegionLatitude=imaging_task.latitude,imagingRegionLongitude=imaging_task.longitude,imagingTime=imaging_task.start_time,deliveryTime=imaging_task.end_time,schedule=get_satelliteSchedule_by_id("admin123_schedule"),startTime=imaging_task.start_time,endTime=imaging_task.end_time, duration=imaging_task.duration)
        i = i+1
    # print("task size: ")
    # print(len(get_all_imagingTask()))

def performingAlgorithumImaginTask():
    #transfer data from DB to algorithm data
    satellites = get_all_satellites()
    imaging_tasks = get_all_imagingTask()
    satelliteDatas = []
    for satellite in satellites:
        activity_window = (satellite.satelliteSchedule.activityWindowStart,satellite.satelliteSchedule.activityWindowEnd)
        satelliteDatas.append(SatelliteData(name=satellite.satelliteId,activity_window=activity_window,tle=satellite.TLE))
    imaging_taskDatas = []
    for imaging_task in imaging_tasks:
        imaging_taskDatas.append(ImageTaskData(name=imaging_task.TaskID,start_time=imaging_task.startTime,end_time=imaging_task.endTime,duration=imaging_task.duration,priority=imaging_task.priority,image_type=ImageTypeData.MEDIUM,latitude=imaging_task.imagingRegionLatitude,longitude=imaging_task.imagingRegionLongitude))
    # print("imaing tasks size: ")
    # print(len(imaging_taskDatas))
    #performing edf
    print('-----------imaging tasks-------------')
    priority_list = group_by_priority(imaging_taskDatas)

    # print_priority_list(priority_list)

    edf(priority_list, satelliteDatas)

    print('------------------')
    total=0
    for satellite in satelliteDatas:
        print(satellite.name, ':')
        total += len(satellite.schedule)
        for t in satellite.schedule:
            print(t[0].name)
    print(f'{total} imaging tasks got scheduled.')

    #transfer data back to database
    for satellite in satelliteDatas:
        for t in satellite.schedule:
            it = get_imagingTask_by_id(t[0].name)
            satellite_schedule = get_satellite_by_id(satellite.name).satelliteSchedule
            updata_imagingTask_info(TaskID=t[0].name,revisitFrequency=it.revisitFrequency,priority=it.priority,imagingRegionLatitude= it.imagingRegionLatitude,imagingRegionLongitude=it.imagingRegionLongitude,imagingTime=it.imagingTime,deliveryTime=it.deliveryTime,schedule=satellite_schedule,startTime=it.startTime,endTime=it.endTime,duration=it.duration)

####################ground station scheduling########################
def sortSatellitesByDeadlineAndTaskPriorityAndNumberOfTasks():
    #find the minimum and maxinum value of number of tasks and sum of priority
    #weight of priority is 10%, wight of number of tasks is 30%, shortest deadline 60%
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
        numberTasks = len(satellite.satelliteSchedule.downlink_tasks) + len(satellite.satelliteSchedule.maintenance_tasks)+len(satellite.satelliteSchedule.imaging_tasks)
        timeTillNow = 0
        for task in satellite.satelliteSchedule.downlink_tasks:
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        for task in satellite.satelliteSchedule.maintenance_tasks:
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        for task in satellite.satelliteSchedule.imaging_tasks:
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
    #normalize each variables and weight them with ratio
    satelliteDic = {}
    for satellite in satellites:
        priority = 0
        numberTasks = len(satellite.satelliteSchedule.downlink_tasks) + len(satellite.satelliteSchedule.maintenance_tasks)+len(satellite.satelliteSchedule.imaging_tasks)
        timeTillNow = 0
        for task in satellite.satelliteSchedule.downlink_tasks:
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        for task in satellite.satelliteSchedule.maintenance_tasks:
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        for task in satellite.satelliteSchedule.imaging_tasks:
            priority = priority + task.priority
            if(task.startTime > now):
                delta = task.startTime - now
                seconds = delta.total_seconds()
                timeTillNow =timeTillNow + seconds
        satelliteDic[satellite] = (0.1*(priority - minPriority)/(maxPriority - minPriority)) + (0.3 * ((numberTasks - minNumberTasks)/(maxNumberTasks - minNumberTasks))) + (-0.6* ((timeTillNow - minTimeTillNow)/(maxTimeTillNow - minTimeTillNow)))
    #sort satellite by the values
    sorted_satellites = sorted(satelliteDic.items(), key=lambda item: item[1], reverse=True)
    #return the sorted satellite
    return sorted_satellites.keys()

def performGroundStationScheduling():
    groundStations = get_all_groundStations()
    satellites = sortSatellitesByDeadlineAndTaskPriorityAndNumberOfTasks()
    now = timezone.now()
    #for each satellites. find the takes place first
    satellitesDic = {}
    for satellite in satellites:
        firstDeadline = timedelta(days=730)
        for task in satellite.satelliteSchedule.downlink_tasks:
            if (task.startTime < firstDeadline):
                firstDeadline = task.startTime
        for task in satellite.satelliteSchedule.maintenance_tasks:
            if (task.startTime < firstDeadline):
                firstDeadline = task.startTime
        for task in satellite.satelliteSchedule.imaging_tasks:
            if (task.startTime < firstDeadline):
                firstDeadline = task.startTime
        satellitesDic[satellite] = firstDeadline

    #put satellite to each ground station    
    timescale = load.timescale()
    for satellite, dl in satellitesDic:
        for groundStation in groundStations:
            s = define_satellite(satellite.TLE)
            g = define_groundstation(groundStation.latitude,groundStation.longitude,groundStation.height)
            startTime = timescale.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
            endTime = timescale.utc(dl.year, dl.month, dl.day, dl.hour, dl.minute, dl.second)
            timeWindows = get_time_window(s,g,startTime,endTime,satellite.fieldOfView)
            if(len(timeWindows)>0):
                add_groundStationRequest(requestId=(groundStation.groundStationId + "request"),acquisitionOfSignal=timeWindows[0][0],lossOfSignal=timeWindows[0][1],satelliteId = satellite.satelliteId,groundStation=groundStation)
                break

    #sort satellites by task priority



