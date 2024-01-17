from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Satellite, SatelliteSchedule, ImagingTask,MaintenanceTask, DownlinkTask,GroundStation, GroundStationRequest, Image, Outage, SatelliteTask
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from .scheduling_algorithm import *


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
def add_SatelliteSchedule(scheduleId, activityWindow, satellite):
    try:
        satelliteSchedule = SatelliteSchedule(scheduleID = scheduleId, activityWindow = activityWindow, satellite = satellite)
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

def update_satelliteSchedule_info(scheduleId, activityWindow, satellite):
    try:
        satelliteSchedule = SatelliteSchedule.objects.get(scheduleID=scheduleId)
        satelliteSchedule.scheduleID = satelliteSchedule.scheduleID
        satelliteSchedule.activityWindow = activityWindow
        satelliteSchedule.satellite = satellite
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
def importTestCaseForScheduling():
    satellites1, satellites2, maintenance_activities, imaging_tasks = initialize_satellites_tasks()
    
