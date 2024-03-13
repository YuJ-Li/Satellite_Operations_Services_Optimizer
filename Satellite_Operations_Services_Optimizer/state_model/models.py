from django.db import models
import json


class Satellite(models.Model):
    name = models.CharField(max_length=50, unique=True)
    maintenance_without_outage = models.TextField(default=json.dumps([]))
    schedule = models.TextField(default=json.dumps([]))
    tle = models.TextField() # Two-Line Element Set Format
    storage_capacity = models.FloatField() # in KB
    capacity_used = models.FloatField() # in kWh



# class SatelliteSchedule(models.Model):
#     satellite = models.OneToOneField(Satellite, on_delete=models.CASCADE,related_name = "satelliteSchedule")
#     scheduleID = models.CharField(max_length=50, unique=True)
#     activityWindowStart = models.DateTimeField()
#     activityWindowEnd = models.DateTimeField()

class SatelliteTask(models.Model):
    name = models.CharField(max_length=50, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    priority = models.PositiveIntegerField()  # Assuming some integer representation
    duration = models.DurationField()
    # satellite = models.ForeignKey(Satellite, on_delete=models.DO_NOTHING, related_name='satellite_tasks')
    class Meta:
        abstract = True  # Indicates this model won't be used to create any database table.

# class Schedule(models.Model):
#     actual_start_time = models.DateTimeField()
#     real_end_time = models.DateTimeField()
#     task_object = models.OneToOneField(SatelliteTask, on_delete=models.CASCADE, related_name="schedule")
#     satellite = models.ForeignKey(Satellite, on_delete=models.CASCADE, related_name='schedules')


# class DownlinkTask(SatelliteTask):
#     imageId = models.CharField(max_length=50, unique=False)
#     #downlinkStartTime = models.DateTimeField()
#     #downlinkEndTime = models.DateTimeField()
#     schedule = models.ForeignKey(SatelliteSchedule, on_delete=models.CASCADE, related_name='downlink_tasks')

class MaintenanceTask(SatelliteTask):
    next_maintenance = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True)
    is_head = models.BooleanField()
    min_gap = models.PositiveIntegerField()
    max_gap = models.PositiveIntegerField()
    payload_outage = models.BooleanField()
    satellite = models.ForeignKey(Satellite, on_delete=models.DO_NOTHING, related_name='maintenance_tasks')
    # target = models.CharField(max_length=255)
    # timeWindow = models.DateTimeField()
    # #duration = models.DurationField()  # Expects a datetime.timedelta instance
    # payloadOperationAffected = models.BooleanField()
    # schedule = models.ForeignKey(SatelliteSchedule, on_delete=models.CASCADE, related_name='maintenance_tasks')

class GroundStation(models.Model):
    groundStationId = models.CharField(max_length=50, unique=True)
    stationName = models.CharField(max_length=100,unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.FloatField()  # assuming in meters
    stationMask = models.CharField(max_length=100)
    uplinkRate = models.FloatField()  # assuming in Mbps
    downlinkRate = models.FloatField()  # assuming in Mbps

class GroundStationRequest(models.Model):
    requestId = models.CharField(max_length=50, unique=True, default=None)
    acquisitionOfSignal = models.DateTimeField()
    lossOfSignal = models.DateTimeField()
    satelliteId = models.CharField(max_length=50)
    groundStation= models.ForeignKey(GroundStation, on_delete=models.CASCADE, related_name='ground_station_requests',default=None)
    

class ImageTask(SatelliteTask):
    image_type = models.CharField(max_length=10)
    imagingRegionLatitude = models.FloatField()
    imagingRegionLongitude = models.FloatField()
    achievability = models.TextField(default=json.dumps({}))
    # satellite = models.ForeignKey(Satellite, on_delete=models.DO_NOTHING, related_name='imaging_tasks')
 
# class Image(models.Model):
#     IMAGE_TYPE_CHOICES = [
#         ('SL', 'Spotlight'),
#         ('MR', 'Medium Resolution'),
#         ('LR', 'Low Resolution'),
#     ]
#     imageId = models.CharField(max_length=50, unique=True)
#     imageSize = models.PositiveIntegerField() # in KB
#     imageType = models.CharField(max_length=2, choices=IMAGE_TYPE_CHOICES)
#     groundStationRequest = models.ForeignKey(GroundStationRequest, on_delete=models.DO_NOTHING, related_name='images')
#     imagingTask = models.ForeignKey(ImagingTask, on_delete=models.DO_NOTHING, related_name='images')


class Outage(models.Model):
    outageId = models.CharField(max_length=50, unique=True,default=None)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    #targets
    groundStation =  models.ForeignKey(GroundStation, on_delete=models.DO_NOTHING, related_name='outages')
    satellite = models.ForeignKey(Satellite, on_delete=models.DO_NOTHING, related_name='outages')