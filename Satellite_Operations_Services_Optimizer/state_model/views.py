from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Satellite, SatelliteSchedule, ImagingTask,MaintenanceTask, DownlinkTask
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

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
        satelliteSchedule = SatelliteSchedule.objects.get(scheduleId)
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
                    imagingRegionLongitude,imagingTime,deliveryTime,schedule):
    try:
        imagingTask = ImagingTask(
            TaskID = TaskID,
            revisitFrequency = revisitFrequency,
            priority = priority,
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
                    imagingRegionLongitude,imagingTime,deliveryTime,schedule):
    try:
        it = ImagingTask.objects.get(TaskID = TaskID)
        it.revisitFrequency = revisitFrequency
        it.priority = priority
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
                        payloadOperationAffected,schedule):
    try:
        maintenanceTask = MaintenanceTask(
            TaskID = TaskID,
            revisitFrequency = revisitFrequency,
            priority = priority,
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
                        payloadOperationAffected,schedule):
    try:
        mt = MaintenanceTask.objects.get(TaskID = TaskID)
        mt.revisitFrequency = revisitFrequency
        mt.priority = priority
        mt.target = target
        mt.timeWindow = timeWindow
        mt.payloadOperationAffected = payloadOperationAffected
        mt.duration = duration
        mt.schedule = schedule
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
def add_downlinkTaskTask(TaskID, revisitFrequency, priority,imageId,downlinkStartTime,downlinkEndTime,schedule):
    try:
        downlinkTask = DownlinkTask(
            TaskID = TaskID,
            revisitFrequency = revisitFrequency,
            priority = priority,
            imageId = imageId,
            downlinkStartTime = downlinkStartTime,
            downlinkEndTime = downlinkEndTime,
            schedule = schedule
        )
        DownlinkTask.save()
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
    
def updata_downlinkTask_info(TaskID, revisitFrequency, priority,imageId,downlinkStartTime,downlinkEndTime,schedule):
    try:
        dt = DownlinkTask.objects.get(TaskID = TaskID)
        dt.revisitFrequency = revisitFrequency
        dt.priority = priority
        dt.imageId=imageId
        dt.downlinkStartTime = downlinkStartTime
        dt.downlinkEndTime = downlinkEndTime
        dt.schedule = schedule
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