from django.utils import timezone
from django.test import TestCase
from .repositories import *
from .models import Satellite, ImageTask, MaintenanceTask, GroundStation, GroundStationRequest, Outage, SatelliteTask
from datetime import timedelta
from django.db import transaction
from django.db import IntegrityError

# class SatelliteControllerTest(TestCase):
#     def test_add_one_satellite_into_database(self):
#         test_satellite =Satellite(satelliteId = "soso1",TLE = "this is a TLE.",storageCapacity = 10,powerCapacity = 10,fieldOfView = 10)
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         satellite = get_satellite_by_id(test_satellite.satelliteId)
#         self.assertEqual(test_satellite.satelliteId,satellite.satelliteId)
#         self.assertEqual(test_satellite.TLE,satellite.TLE)
#         self.assertEqual(test_satellite.storageCapacity,satellite.storageCapacity)
#         self.assertEqual(test_satellite.powerCapacity,satellite.powerCapacity)
#         self.assertEqual(test_satellite.fieldOfView,satellite.fieldOfView)
#     def test_get_all_satellite_from_database(self):
#         number_of_satellite = 5
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_satellite("soso2","this is a TLE.",10,10,10)
#         add_satellite("soso3","this is a TLE.",10,10,10)
#         add_satellite("soso4","this is a TLE.",10,10,10)
#         add_satellite("soso5","this is a TLE.",10,10,10)
#         self.assertEqual(len(get_all_satellites()),number_of_satellite)
#     def test_delete_satellite_by_id_from_database(self):
#         number_of_satellite = 4
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_satellite("soso2","this is a TLE.",10,10,10)
#         add_satellite("soso3","this is a TLE.",10,10,10)
#         add_satellite("soso4","this is a TLE.",10,10,10)
#         add_satellite("soso5","this is a TLE.",10,10,10)
#         delete_satellite_by_id("soso3")
#         self.assertEqual(len(get_all_satellites()),number_of_satellite)
#     def test_update_satellite_info_to_database(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         # satelliteSchedule = SatelliteSchedule(scheduleID = "station1",satellite = get_satellite_by_id("soso1"),activityWindow=timezone.now())
#         # satelliteSchedule.save()
#         update_satellite_info(
#                             satellite_id = "soso1",
#                             TLE = "this is a TLE2.", 
#                             storageCapacity = 10, 
#                             powerCapacity = 10, 
#                             fieldOfView = 10,
#                             #satelliteSchedule = satelliteSchedule
#                             )
#         satellite = get_satellite_by_id("soso1")
#         self.assertEqual(satellite.TLE,"this is a TLE2.")

# class SatelliteScheduleControllerTest(TestCase):
#     def test_add_one_satellite_schedule_into_database(self):
#         test_satellite =Satellite(satelliteId = "soso1",TLE = "this is a TLE.",storageCapacity = 10,powerCapacity = 10,fieldOfView = 10)
#         test_satellite.save()
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=test_satellite)
#         schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne")
#         self.assertEqual(schedule.scheduleID,"scheduleOne")
#     def test_get_all_schedule_from_database(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_satellite("soso2","this is a TLE.",10,10,10)
#         add_satellite("soso3","this is a TLE.",10,10,10)
#         add_satellite("soso4","this is a TLE.",10,10,10)
#         add_satellite("soso5","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_SatelliteSchedule(scheduleId ="scheduleTwo",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso2"))
#         add_SatelliteSchedule(scheduleId ="scheduleThree",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso3"))
#         add_SatelliteSchedule(scheduleId ="scheduleFour",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso4"))
#         add_SatelliteSchedule(scheduleId ="scheduleFive",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso5"))
#         self.assertAlmostEqual(len(get_all_satelliteSchedules()),5)
#     def test_delete_schedule_from_database(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_satellite("soso2","this is a TLE.",10,10,10)
#         add_satellite("soso3","this is a TLE.",10,10,10)
#         add_satellite("soso4","this is a TLE.",10,10,10)
#         add_satellite("soso5","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_SatelliteSchedule(scheduleId ="scheduleTwo",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso2"))
#         add_SatelliteSchedule(scheduleId ="scheduleThree",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso3"))
#         add_SatelliteSchedule(scheduleId ="scheduleFour",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso4"))
#         add_SatelliteSchedule(scheduleId ="scheduleFive",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso5"))
#         delete_satelliteSchedule_by_id("scheduleThree")
#         self.assertAlmostEqual(len(get_all_satelliteSchedules()),4)
#     def test_update_schedule_info(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_satellite("soso2","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         update_satelliteSchedule_info(scheduleId= "scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso2"))
#         self.assertEqual(get_satelliteSchedule_by_id("scheduleOne").satellite.satelliteId,"soso2")
#     def test_relationship_schedule_satellite_exist(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         self.assertEqual(get_satellite_by_id("soso1").satelliteSchedule.scheduleID,"scheduleOne")

# class ImageTaskControllerTest(TestCase):
#     def test_add_one_imageTask_schedule_into_database(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         imageTask = get_imagingTask_by_id("imageTask1")
#         self.assertEqual(imageTask.TaskID,"imageTask1")
#     def test_get_all_imageTask(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         add_imagingTask(TaskID = "imageTask2",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         add_imagingTask(TaskID = "imageTask3",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         add_imagingTask(TaskID = "imageTask4",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         self.assertEqual(len(get_all_imagingTask()),4)
#     def test_delete_imageTask(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         add_imagingTask(TaskID = "imageTask2",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         add_imagingTask(TaskID = "imageTask3",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         add_imagingTask(TaskID = "imageTask4",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         delete_imagingTask_by_id("imageTask3")
#         self.assertEqual(len(get_all_imagingTask()),3)
#     def test_update_imageTask_info(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         updata_imagingTask_info(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 12,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         self.assertEqual(get_imagingTask_by_id("imageTask1").imagingRegionLongitude,12)
#     def test_imageTask_SatelliteSchedule_relationship(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         self.assertEqual(get_satelliteSchedule_by_id("scheduleOne").imaging_tasks.get(TaskID = "imageTask1").TaskID,"imageTask1")
#     def test_imageTask_SatelliteSchedule_relationship_after_update_schedule(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_satellite("soso2","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         self.assertEqual(get_satelliteSchedule_by_id("scheduleOne").imaging_tasks.get(TaskID = "imageTask1").TaskID,"imageTask1")
#         add_SatelliteSchedule(scheduleId ="scheduleTwo",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso2"))
#         updata_imagingTask_info(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 12,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleTwo"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
#         self.assertEqual(get_satelliteSchedule_by_id("scheduleTwo").imaging_tasks.get(TaskID = "imageTask1").TaskID,"imageTask1")
#         #self.assertEqual(get_satelliteSchedule_by_id("scheduleOne").imaging_tasks.get(TaskID = "imageTask1").TaskID,"imageTask1")
# class MaintenanceTaskControllerTest(TestCase):
#     def test_add_one_maintenanceTask_schedule_into_database(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_maintenanceTask(TaskID = "maintenanceTask1",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = True,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         mt = get_maintenanceTask_by_id(TaskID = "maintenanceTask1")
#         self.assertEqual(mt.TaskID,"maintenanceTask1")
#     def test_get_all_maintenanceTask(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_maintenanceTask(TaskID = "maintenanceTask1",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = True,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         add_maintenanceTask(TaskID = "maintenanceTask2",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = True,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         add_maintenanceTask(TaskID = "maintenanceTask3",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = True,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         add_maintenanceTask(TaskID = "maintenanceTask4",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = True,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         self.assertEqual(len(get_all_maintenanceTask()),4)
#     def test_update_maintenanceTask_info(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_maintenanceTask(TaskID = "maintenanceTask1",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = True,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         updata_maintenanceTask_info(TaskID = "maintenanceTask1",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = False,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         self.assertEqual(get_maintenanceTask_by_id("maintenanceTask1").payloadOperationAffected,False)
#     def test_delete_maintenanceTask(self):
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
#         add_maintenanceTask(TaskID = "maintenanceTask1",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = True,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         add_maintenanceTask(TaskID = "maintenanceTask2",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = True,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         add_maintenanceTask(TaskID = "maintenanceTask3",revisitFrequency = 2,priority=10,target = "target1",timeWindow = timezone.now(),duration =timedelta(hours=1, minutes=15), payloadOperationAffected = True,schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now())
#         delete_maintenanceTask_by_id("maintenanceTask3")
#         self.assertEqual(len(get_all_maintenanceTask()),2)
#         self.assertEqual(get_satelliteSchedule_by_id("scheduleOne").maintenance_tasks.get(TaskID = "maintenanceTask2").TaskID,"maintenanceTask2")

# # class DownlinkTaskControllerTest(TestCase):
# #     def test_add_one_downlinkTask_schedule_into_database(self):
# #         add_satellite("soso1","this is a TLE.",10,10,10)
# #         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
# #         add_downlinkTaskTask(TaskID="dTask1",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         self.assertEqual(get_downlinkTask_by_id("dTask1").TaskID,"dTask1")
# #         self.assertEqual(get_satelliteSchedule_by_id("scheduleOne").downlink_tasks.get(TaskID = "dTask1").TaskID,"dTask1")
    
# #     def test_get_all_downlinkTask(self):
# #         add_satellite("soso1","this is a TLE.",10,10,10)
# #         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
# #         add_downlinkTaskTask(TaskID="dTask1",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         add_downlinkTaskTask(TaskID="dTask2",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         add_downlinkTaskTask(TaskID="dTask3",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         add_downlinkTaskTask(TaskID="dTask4",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         self.assertEqual(len(get_all_downlinkTask()),4)

# #     def test_delete_downlinkTask(self):
# #         add_satellite("soso1","this is a TLE.",10,10,10)
# #         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
# #         add_downlinkTaskTask(TaskID="dTask1",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         add_downlinkTaskTask(TaskID="dTask2",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         add_downlinkTaskTask(TaskID="dTask3",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         add_downlinkTaskTask(TaskID="dTask4",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         delete_downlinkTask_by_id("dTask4")
# #         self.assertEqual(len(get_all_downlinkTask()),3)

# #     def test_update_downlinkTask(self):
# #         add_satellite("soso1","this is a TLE.",10,10,10)
# #         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
# #         add_downlinkTaskTask(TaskID="dTask1",revisitFrequency=24,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         update_downlinkTask_info(TaskID="dTask1",revisitFrequency=25,priority=1,imageId="image1",startTime=timezone.now(),endTime=timezone.now(),schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne"),duration =timedelta(hours=1, minutes=15))
# #         self.assertEqual(get_downlinkTask_by_id("dTask1").revisitFrequency,25)

# class GroundStationControllerTests(TestCase):
#     def test_add_groundStation_to_db(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         self.assertEqual(get_groundStation_by_id("groundStation1").groundStationId,"groundStation1")
#     def test_get_all_groundStation(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStation(
#             groundStationId="groundStation2",
#             stationName="Sample Ground Station2",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStation(
#             groundStationId="groundStation3",
#             stationName="Sample Ground Station3",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         self.assertEqual(len(get_all_groundStations()),3)
#     def test_delete_groundStation(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStation(
#             groundStationId="groundStation2",
#             stationName="Sample Ground Station2",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStation(
#             groundStationId="groundStation3",
#             stationName="Sample Ground Station3",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         delete_groundStation_by_id("groundStation3")
#         self.assertEqual(len(get_all_groundStations()),2)
#     def test_update_groundStation(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200
#         )
#         update_groundStation_info(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=300, 
#             downlinkRate=200
#         )
#         self.assertEqual(get_groundStation_by_id("groundStation1").uplinkRate,300)
    
# class GroundStationRequestControllerTests(TestCase):
#     def test_add_groundStationRequest_to_db(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStationRequest(
#             requestId="request1",
#             acquisitionOfSignal="2023-10-25 10:00:00",
#             lossOfSignal="2023-10-25 11:00:00", 
#             satelliteId="SAT123",
#             groundStation=get_groundStation_by_id("groundStation1")
#         )
#         self.assertEqual(get_groundStationRequest_by_id("request1").requestId,"request1")
#         self.assertEqual(get_groundStation_by_id("groundStation1").ground_station_requests.get(requestId="request1").requestId,"request1")
#     def test_get_all_groundstation_requests(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStationRequest(
#             requestId="request1",
#             acquisitionOfSignal="2023-10-25 10:00:00",
#             lossOfSignal="2023-10-25 11:00:00", 
#             satelliteId="SAT123",
#             groundStation=get_groundStation_by_id("groundStation1")
#         )
#         add_groundStationRequest(
#             requestId="request2",
#             acquisitionOfSignal="2023-10-25 10:00:00",
#             lossOfSignal="2023-10-25 11:00:00", 
#             satelliteId="SAT123",
#             groundStation=get_groundStation_by_id("groundStation1")
#         )
#         add_groundStationRequest(
#             requestId="request3",
#             acquisitionOfSignal="2023-10-25 10:00:00",
#             lossOfSignal="2023-10-25 11:00:00", 
#             satelliteId="SAT123",
#             groundStation=get_groundStation_by_id("groundStation1")
#         )
#         self.assertEqual(len(get_all_groundStationRequest()),3)
#     def test_delete_groundstation_requests(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStationRequest(
#             requestId="request1",
#             acquisitionOfSignal="2023-10-25 10:00:00",
#             lossOfSignal="2023-10-25 11:00:00", 
#             satelliteId="SAT123",
#             groundStation=get_groundStation_by_id("groundStation1")
#         )
#         add_groundStationRequest(
#             requestId="request2",
#             acquisitionOfSignal="2023-10-25 10:00:00",
#             lossOfSignal="2023-10-25 11:00:00", 
#             satelliteId="SAT123",
#             groundStation=get_groundStation_by_id("groundStation1")
#         )
#         add_groundStationRequest(
#             requestId="request3",
#             acquisitionOfSignal="2023-10-25 10:00:00",
#             lossOfSignal="2023-10-25 11:00:00", 
#             satelliteId="SAT123",
#             groundStation=get_groundStation_by_id("groundStation1")
#         )
#         delete_groundStationRequest_by_id("request3")
#         self.assertEqual(len(get_all_groundStationRequest()),2)
#     def test_update_groundstation_requests(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStationRequest(
#             requestId="request1",
#             acquisitionOfSignal="2023-10-25 10:00:00",
#             lossOfSignal="2023-10-25 11:00:00", 
#             satelliteId="SAT123",
#             groundStation=get_groundStation_by_id("groundStation1")
#         )
#         update_groundStationRequest_info(      
#             requestId="request1",
#             acquisitionOfSignal="2023-10-25 10:00:00",
#             lossOfSignal="2023-10-25 11:00:00", 
#             satelliteId="SAT1234",
#             groundStation=get_groundStation_by_id("groundStation1")
#         )
#         self.assertEqual(get_groundStationRequest_by_id("request1").satelliteId,"SAT1234")

# class OutageControllerTest(TestCase):
#     def test_add_outage(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_outage(outageId="outage1",startTime=timezone.now(),endTime=timezone.now(),groundStation=get_groundStation_by_id("groundStation1"),satellite=get_satellite_by_id("soso1"))
#         self.assertEqual(get_outage_by_id("outage1").outageId,"outage1")
#         self.assertEqual(get_groundStation_by_id("groundStation1").outages.get(outageId="outage1").outageId,"outage1")
#         self.assertEqual(get_satellite_by_id("soso1").outages.get(outageId="outage1").outageId,"outage1")
#     def test_get_all_outage(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_outage(outageId="outage1",startTime=timezone.now(),endTime=timezone.now(),groundStation=get_groundStation_by_id("groundStation1"),satellite=get_satellite_by_id("soso1"))
#         add_outage(outageId="outage2",startTime=timezone.now(),endTime=timezone.now(),groundStation=get_groundStation_by_id("groundStation1"),satellite=get_satellite_by_id("soso1"))
#         add_outage(outageId="outage3",startTime=timezone.now(),endTime=timezone.now(),groundStation=get_groundStation_by_id("groundStation1"),satellite=get_satellite_by_id("soso1"))
#         self.assertEqual(len(get_all_outage()),3)
#     def test_delete_outage(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_outage(outageId="outage1",startTime=timezone.now(),endTime=timezone.now(),groundStation=get_groundStation_by_id("groundStation1"),satellite=get_satellite_by_id("soso1"))
#         add_outage(outageId="outage2",startTime=timezone.now(),endTime=timezone.now(),groundStation=get_groundStation_by_id("groundStation1"),satellite=get_satellite_by_id("soso1"))
#         add_outage(outageId="outage3",startTime=timezone.now(),endTime=timezone.now(),groundStation=get_groundStation_by_id("groundStation1"),satellite=get_satellite_by_id("soso1"))
#         delete_outage_by_id("outage1")
#         self.assertEqual(len(get_all_outage()),2)

#     def test_update_outage(self):
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=34.0522,
#             longitude=-118.2437,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_satellite("soso1","this is a TLE.",10,10,10)
#         add_satellite("soso2","this is a TLE.",10,10,10)
#         add_outage(outageId="outage1",startTime=timezone.now(),endTime=timezone.now(),groundStation=get_groundStation_by_id("groundStation1"),satellite=get_satellite_by_id("soso1"))
#         update_outage_info(outageId="outage1",startTime=timezone.now(),endTime=timezone.now(),groundStation=get_groundStation_by_id("groundStation1"),satellite=get_satellite_by_id("soso2"))
#         self.assertEqual(get_outage_by_id("outage1").satellite.satelliteId,"soso2")

# # class ImageControllerTest(TestCase):
# #     def test_add_image(self):
# #         add_groundStation(
# #             groundStationId="groundStation1",
# #             stationName="Sample Ground Station1",
# #             latitude=34.0522,
# #             longitude=-118.2437,
# #             height=500, 
# #             stationMask="255.255.255.0", 
# #             uplinkRate=100, 
# #             downlinkRate=200, 
# #         )
# #         add_groundStationRequest(
# #             requestId="request1",
# #             acquisitionOfSignal="2023-10-25 10:00:00",
# #             lossOfSignal="2023-10-25 11:00:00", 
# #             satelliteId="SAT123",
# #             groundStation=get_groundStation_by_id("groundStation1")
# #         )
# #         add_satellite("soso1","this is a TLE.",10,10,10)
# #         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
# #         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now(),duration =timedelta(hours=1, minutes=15))
# #         add_image(
# #             imageId="image1",  
# #             imageSize=1024, 
# #             imageType="SL",  
# #             groundStationRequest=get_groundStationRequest_by_id("request1"),  
# #             imagingTask=get_imagingTask_by_id("imageTask1")
# #         )
# #         self.assertEqual(get_image_by_id("image1").imageId,"image1")
# #     def test_get_all_image(self):
# #         add_groundStation(
# #             groundStationId="groundStation1",
# #             stationName="Sample Ground Station1",
# #             latitude=34.0522,
# #             longitude=-118.2437,
# #             height=500, 
# #             stationMask="255.255.255.0", 
# #             uplinkRate=100, 
# #             downlinkRate=200, 
# #         )
# #         add_groundStationRequest(
# #             requestId="request1",
# #             acquisitionOfSignal="2023-10-25 10:00:00",
# #             lossOfSignal="2023-10-25 11:00:00", 
# #             satelliteId="SAT123",
# #             groundStation=get_groundStation_by_id("groundStation1")
# #         )
# #         add_satellite("soso1","this is a TLE.",10,10,10)
# #         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
# #         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
# #         add_imagingTask(TaskID = "imageTask2",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
# #         add_image(
# #             imageId="image1",  
# #             imageSize=1024, 
# #             imageType="SL",  
# #             groundStationRequest=get_groundStationRequest_by_id("request1"),  
# #             imagingTask=get_imagingTask_by_id("imageTask1")
# #         )
      
# #         add_image(
# #             imageId="image2",  
# #             imageSize=1024, 
# #             imageType="SL",  
# #             groundStationRequest=get_groundStationRequest_by_id("request1"),  
# #             imagingTask=get_imagingTask_by_id("imageTask2")
# #         )
        
# #         self.assertEqual(len(get_all_images()),2)

# #     def test_delete_image(self):
# #         add_groundStation(
# #             groundStationId="groundStation1",
# #             stationName="Sample Ground Station1",
# #             latitude=34.0522,
# #             longitude=-118.2437,
# #             height=500, 
# #             stationMask="255.255.255.0", 
# #             uplinkRate=100, 
# #             downlinkRate=200, 
# #         )
# #         add_groundStationRequest(
# #             requestId="request1",
# #             acquisitionOfSignal="2023-10-25 10:00:00",
# #             lossOfSignal="2023-10-25 11:00:00", 
# #             satelliteId="SAT123",
# #             groundStation=get_groundStation_by_id("groundStation1")
# #         )
# #         add_satellite("soso1","this is a TLE.",10,10,10)
# #         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
# #         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now(),duration =timedelta(hours=1, minutes=15))
# #         add_imagingTask(TaskID = "imageTask2",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(),endTime=timezone.now(),duration =timedelta(hours=1, minutes=15))
# #         add_image(
# #             imageId="image1",  
# #             imageSize=1024, 
# #             imageType="SL",  
# #             groundStationRequest=get_groundStationRequest_by_id("request1"),  
# #             imagingTask=get_imagingTask_by_id("imageTask1")
# #         )
      
# #         add_image(
# #             imageId="image2",  
# #             imageSize=1024, 
# #             imageType="SL",  
# #             groundStationRequest=get_groundStationRequest_by_id("request1"),  
# #             imagingTask=get_imagingTask_by_id("imageTask2")
# #         )
# #         delete_image_by_id("image1")
# #         self.assertEqual(len(get_all_images()),1)

# #     def test_update_image(self):
# #         add_groundStation(
# #             groundStationId="groundStation1",
# #             stationName="Sample Ground Station1",
# #             latitude=34.0522,
# #             longitude=-118.2437,
# #             height=500, 
# #             stationMask="255.255.255.0", 
# #             uplinkRate=100, 
# #             downlinkRate=200, 
# #         )
# #         add_groundStationRequest(
# #             requestId="request1",
# #             acquisitionOfSignal="2023-10-25 10:00:00",
# #             lossOfSignal="2023-10-25 11:00:00", 
# #             satelliteId="SAT123",
# #             groundStation=get_groundStation_by_id("groundStation1")
# #         )
# #         add_satellite("soso1","this is a TLE.",10,10,10)
# #         add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindowStart=timezone.now(),activityWindowEnd=timezone.now(),satellite=get_satellite_by_id("soso1"))
# #         add_imagingTask(TaskID = "imageTask1",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
# #         add_imagingTask(TaskID = "imageTask2",revisitFrequency = 2,priority=10,imagingRegionLatitude = 10,imagingRegionLongitude = 10,imagingTime=timezone.now(),deliveryTime = timezone.now(),schedule = get_satelliteSchedule_by_id("scheduleOne"),startTime=timezone.now(), endTime=timezone.now(),duration = timedelta(hours=1, minutes=15))
# #         add_image(
# #             imageId="image1",  
# #             imageSize=1024, 
# #             imageType="SL",  
# #             groundStationRequest=get_groundStationRequest_by_id("request1"),  
# #             imagingTask=get_imagingTask_by_id("imageTask1")
# #         )
# #         update_image_info(
# #             imageId="image1",  
# #             imageSize=2048, 
# #             imageType="SL",  
# #             groundStationRequest=get_groundStationRequest_by_id("request1"),  
# #             imagingTask=get_imagingTask_by_id("imageTask1")
# #         )
# #         self.assertEqual(get_image_by_id("image1").imageSize,2048)

class TestSatelliteSchedulingAlgorithum(TestCase):
    
    def test_import_test_cases(self):
        importTestCaseForSchedulingImagingTask("/app/order_samples/group2")

        ss = get_all_satellites()
        self.assertEqual(len(ss),5)
        self.assertEqual(len(get_all_imageTask()),135) # group2 contains 135 imaging tasks including revisits


    def test_transferDataToAlgorithum(self):
        importTestCaseForSchedulingImagingTask("/app/order_samples/group4_newest")
        total_scheduled_tasks = performingAlgorithumImaginTask()
        # print("all satellites: #############")
        # print(get_all_imagingTask()[0].TaskID)
        # print(get_all_imagingTask()[0].schedule.satellite.satelliteId)
        # print(get_all_imagingTask()[1].TaskID)
        # print(get_all_imagingTask()[1].schedule.satellite.satelliteId)
        # print(get_all_imagingTask()[2].TaskID)
        # print(get_all_imagingTask()[2].schedule.satellite.satelliteId)
        #print(get_all_satellites()[0].satelliteSchedule.imaging_tasks.get(TaskID = "ImagingTask10").TaskID)
        self.assertGreater(total_scheduled_tasks,0)
        
# class TestGroundStationSchedulingAlgorithum(TestCase):
#     def test_import_test_cases(self):
#         importTestCaseForSchedulingImagingTask("/app/order_samples/group3")
#         self.assertEqual(len(get_all_satellites()),6)
#         self.assertEqual(len(get_all_imagingTask()),30)
#     def test_sortSatellitesByDeadlineAndTaskPriorityAndNumberOfTasks(self):
#         importTestCaseForSchedulingImagingTask("/app/order_samples/group3")
#         performingAlgorithumImaginTask()
#         print(sortSatellitesByDeadlineAndTaskPriorityAndNumberOfTasks())
#         self.assertEqual(len(sortSatellitesByDeadlineAndTaskPriorityAndNumberOfTasks()),6)
#     def test_performGroundStationScheduling(self):
#         print("#######ground sataion scheduling##################")
#         importTestCaseForSchedulingImagingTask("/app/order_samples/group3")
#         add_groundStation(
#             groundStationId="groundStation1",
#             stationName="Sample Ground Station1",
#             latitude=-79.92044865279952, #
#             longitude=-27.567082165241743,
#             height=500, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStation(
#             groundStationId="groundStation2",
#             stationName="Sample Ground Station2",
#             latitude=-85.6439118846981,
#             longitude=-52.678023392885535,
#             height=300, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         add_groundStation(
#             groundStationId="groundStation3",
#             stationName="Sample Ground Station3",
#             latitude=-3.0093935327252694,
#             longitude=-43.491089830886835,
#             height=100, 
#             stationMask="255.255.255.0", 
#             uplinkRate=100, 
#             downlinkRate=200, 
#         )
#         performingAlgorithumImaginTask()
#         performGroundStationScheduling()
