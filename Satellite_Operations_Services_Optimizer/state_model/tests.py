from django.utils import timezone
from datetime import datetime
from django.test import TestCase
from .views import add_satellite, get_satellite_by_id,get_all_satellites, delete_satellite_by_id, update_satellite_info
from .models import Satellite, SatelliteSchedule
# Create your tests here.
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
        satelliteSchedule = SatelliteSchedule(scheduleID = "station1",satellite = get_satellite_by_id("soso1"),activityWindow=timezone.now())
        satelliteSchedule.save()
        update_satellite_info(
                            satellite_id = "soso1",
                            TLE = "this is a TLE2.", 
                            storageCapacity = 10, 
                            powerCapacity = 10, 
                            fieldOfView = 10,
                            satelliteSchedule = satelliteSchedule
                            )
        satellite = get_satellite_by_id("soso1")
        self.assertEqual(satellite.TLE,"this is a TLE2.")
        self.assertEqual(satellite.satelliteSchedule.scheduleID,"station1")
        
