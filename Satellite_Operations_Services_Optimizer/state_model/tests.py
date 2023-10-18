from django.utils import timezone
from datetime import datetime
from django.test import TestCase
from .views import add_satellite, get_satellite_by_id,get_all_satellites, delete_satellite_by_id, update_satellite_info, add_SatelliteSchedule,get_satelliteSchedule_by_id,get_all_satelliteSchedules,delete_satelliteSchedule_by_id,update_satelliteSchedule_info
from .models import Satellite, SatelliteSchedule

class SatelliteControllerTest(TestCase):
    def test_add_one_satellite_into_database(self):
        test_satellite =Satellite(satelliteId = "soso1",TLE = "this is a TLE.",storageCapacity = 10,powerCapacity = 10,fieldOfView = 10)
        add_satellite("soso1","this is a TLE.",10,10,10)
        satellite = get_satellite_by_id(test_satellite.satelliteId)
        self.assertEqual(test_satellite.satelliteId,satellite.satelliteId)
        self.assertEqual(test_satellite.TLE,satellite.TLE)
        self.assertEqual(test_satellite.storageCapacity,satellite.storageCapacity)
        self.assertEqual(test_satellite.powerCapacity,satellite.powerCapacity)
        self.assertEqual(test_satellite.fieldOfView,satellite.fieldOfView)
    def test_get_all_satellite_from_database(self):
        number_of_satellite = 5
        add_satellite("soso1","this is a TLE.",10,10,10)
        add_satellite("soso2","this is a TLE.",10,10,10)
        add_satellite("soso3","this is a TLE.",10,10,10)
        add_satellite("soso4","this is a TLE.",10,10,10)
        add_satellite("soso5","this is a TLE.",10,10,10)
        self.assertEqual(len(get_all_satellites()),number_of_satellite)
    def test_delete_satellite_by_id_from_database(self):
        number_of_satellite = 4
        add_satellite("soso1","this is a TLE.",10,10,10)
        add_satellite("soso2","this is a TLE.",10,10,10)
        add_satellite("soso3","this is a TLE.",10,10,10)
        add_satellite("soso4","this is a TLE.",10,10,10)
        add_satellite("soso5","this is a TLE.",10,10,10)
        delete_satellite_by_id("soso3")
        self.assertEqual(len(get_all_satellites()),number_of_satellite)
    def test_update_satellite_info_to_database(self):
        add_satellite("soso1","this is a TLE.",10,10,10)
        # satelliteSchedule = SatelliteSchedule(scheduleID = "station1",satellite = get_satellite_by_id("soso1"),activityWindow=timezone.now())
        # satelliteSchedule.save()
        update_satellite_info(
                            satellite_id = "soso1",
                            TLE = "this is a TLE2.", 
                            storageCapacity = 10, 
                            powerCapacity = 10, 
                            fieldOfView = 10,
                            #satelliteSchedule = satelliteSchedule
                            )
        satellite = get_satellite_by_id("soso1")
        self.assertEqual(satellite.TLE,"this is a TLE2.")

class SatelliteScheduleControllerTest(TestCase):
    def test_add_one_satellite_schedule_into_database(self):
        test_satellite =Satellite(satelliteId = "soso1",TLE = "this is a TLE.",storageCapacity = 10,powerCapacity = 10,fieldOfView = 10)
        test_satellite.save()
        add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindow=timezone.now(),satellite=test_satellite)
        schedule = get_satelliteSchedule_by_id(scheduleId ="scheduleOne")
        self.assertEqual(schedule.scheduleID,"scheduleOne")
    def test_get_all_schedule_from_database(self):
        add_satellite("soso1","this is a TLE.",10,10,10)
        add_satellite("soso2","this is a TLE.",10,10,10)
        add_satellite("soso3","this is a TLE.",10,10,10)
        add_satellite("soso4","this is a TLE.",10,10,10)
        add_satellite("soso5","this is a TLE.",10,10,10)
        add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso1"))
        add_SatelliteSchedule(scheduleId ="scheduleTwo",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso2"))
        add_SatelliteSchedule(scheduleId ="scheduleThree",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso3"))
        add_SatelliteSchedule(scheduleId ="scheduleFour",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso4"))
        add_SatelliteSchedule(scheduleId ="scheduleFive",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso5"))
        self.assertAlmostEqual(len(get_all_satelliteSchedules()),5)
    def test_delete_schedule_from_database(self):
        add_satellite("soso1","this is a TLE.",10,10,10)
        add_satellite("soso2","this is a TLE.",10,10,10)
        add_satellite("soso3","this is a TLE.",10,10,10)
        add_satellite("soso4","this is a TLE.",10,10,10)
        add_satellite("soso5","this is a TLE.",10,10,10)
        add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso1"))
        add_SatelliteSchedule(scheduleId ="scheduleTwo",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso2"))
        add_SatelliteSchedule(scheduleId ="scheduleThree",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso3"))
        add_SatelliteSchedule(scheduleId ="scheduleFour",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso4"))
        add_SatelliteSchedule(scheduleId ="scheduleFive",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso5"))
        delete_satelliteSchedule_by_id("scheduleThree")
        self.assertAlmostEqual(len(get_all_satelliteSchedules()),4)
    def test_relationship_schedule_satellite_exist(self):
        add_satellite("soso1","this is a TLE.",10,10,10)
        add_SatelliteSchedule(scheduleId ="scheduleOne",activityWindow=timezone.now(),satellite=get_satellite_by_id("soso1"))
        self.assertEqual(get_satellite_by_id("soso1").satelliteSchedule.scheduleID,"scheduleOne")