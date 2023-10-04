from django.db import models

class Satellite(models.Model):
    satelliteId = models.CharField(max_length=50, unique=True)
    TLE = models.TextField() # Two-Line Element Set Format
    storageCapacity = models.FloatField() # in GB
    powerCapacity = models.FloatField() # in kWh
    fieldOfView = models.FloatField() # in degrees

class SatelliteSchedule(models.Model):
    satellite = models.ForeignKey(Satellite, on_delete=models.CASCADE, related_name='schedules')
    scheduleID = models.CharField(max_length=50, unique=True)
    activityWindow = models.DateTimeField()
    satellite = models.ForeignKey(Satellite, related_name='schedules', on_delete=models.CASCADE)

class SatelliteTask(models.Model):
    TaskID = models.CharField(max_length=50, unique=True)
    revisitFrequency = models.PositiveIntegerField()  # In some time unit (e.g., hours, days)
    priority = models.PositiveIntegerField()  # Assuming some integer representation

    class Meta:
        abstract = True  # Indicates this model won't be used to create any database table.

class DownlinkTask(SatelliteTask):
    imageId = models.CharField(max_length=50)
    downlinkStartTime = models.DateTimeField()
    downlinkEndTime = models.DateTimeField()
    schedule = models.ForeignKey(SatelliteSchedule, on_delete=models.CASCADE, related_name='downlink_tasks')

class MaintenanceTask(SatelliteTask):
    target = models.CharField(max_length=255)
    timeWindow = models.DateTimeField()
    duration = models.DurationField()  # Expects a datetime.timedelta instance
    payloadOperationAffected = models.BooleanField()
    schedule = models.ForeignKey(SatelliteSchedule, on_delete=models.CASCADE, related_name='maintenance_tasks')
class ImagingTask(SatelliteTask):
    IMAGE_TYPE_CHOICES = [
        ('SL', 'Spotlight'),
        ('MR', 'Medium Resolution'),
        ('LR', 'Low Resolution'),
    ]
    
    imagingRegionLatitude = models.FloatField()
    imagingRegionLongitude = models.FloatField()
    imagingTime = models.DateTimeField()
    imageType = models.CharField(max_length=2, choices=IMAGE_TYPE_CHOICES)
    deliveryTime = models.DateTimeField()
    schedule = models.ForeignKey(SatelliteSchedule, on_delete=models.CASCADE, related_name='imaging_tasks')

class GroundStation(models.Model):
    groundStationId = models.CharField(max_length=50, unique=True)
    stationName = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.FloatField()  # assuming in meters
    stationMask = models.CharField(max_length=100)
    uplinkRate = models.FloatField()  # assuming in Mbps
    downlinkRate = models.FloatField()  # assuming in Mbps

class GroundStationRequest(models.Model):
    stationName = models.CharField(max_length=100)
    satellite = models.ForeignKey(Satellite, on_delete=models.CASCADE, related_name='ground_station_requests')
    acquisitionOfSignal = models.DateTimeField()
    lossOfSignal = models.DateTimeField()
    satelliteScheduleId = models.CharField(max_length=50)
    imagesDownlinked = models.CharField(max_length=100)  # [imageID:, durationOfDownlink:, imageSize:]