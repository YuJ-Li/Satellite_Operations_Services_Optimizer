from django.test import TestCase
from .views import add_satellite, get_satellite_by_id
from .models import Satellite
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
