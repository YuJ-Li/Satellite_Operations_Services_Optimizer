from datetime import datetime
import datetime as dt
import json
import os
from enum import Enum

###################################### CLASSES ###########################################

class Task:
    def __init__(self, name, start_time, end_time, duration, priority, satellite = None):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.priority = priority # imaging tasks: priority from 3 to 1 = from high to low; maintenance activity: priority = 4 (highest)
        self.satellite = satellite # to be determined by the scheduling algorithm

class Satellite:
    def __init__(self, name, activity_window):
        self.name = name
        self.activity_window = activity_window
        self.schedule = [] # list of ((#task_name, actual_start_time, real_end_time))

class ImageTask(Task):
    def __init__(self, image_type, name, start_time, end_time, duration, priority, satellite = None):
        super().__init__(name = name, start_time = start_time, end_time = end_time, duration = duration, priority = priority, satellite = satellite)
        self.image_type = image_type

class ImageType(Enum):
    SPOTLIGHT = {'time_for_writing':120, 'size':512, 'dimension':[10,10]}
    MEDIUM = {'time_for_writing':45, 'size':256, 'dimension':[40,20]}
    LOW = {'time_for_writing':20, 'size':128, 'dimension':[40,20]}


######################################## General functions ##########################################

def read_directory(path):
    json_files = [f.path for f in os.scandir(path) if f.is_file() and f.name.endswith(('.json', '.JSON'))]
    return json_files

def convert_str_to_datetime(datetime_str):
    date_and_time = datetime_str.split('T')
    arr = date_and_time[0].split('-')
    arr.extend(date_and_time[1].split(':'))
    datetime_obj = datetime(int(arr[0]),int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]),int(arr[5]))
    return datetime_obj

def get_image_type(image_type):
    match image_type:
        case "Low":
            return ImageType.LOW
        case "Medium":
            return ImageType.MEDIUM
        case "Spotlight":
            return ImageType.SPOTLIGHT
        
def get_satellite_by_name(satellites, name):
    for satellite in satellites:
        if satellite.name == name:
            return satellite
    return None

def check_task_achievability_on_satellite(Tasks, Satellites):

    return False

############################### Initialize satellites ################################
time_window_start = datetime(2023, 10, 8, 00, 00, 00)
time_window_end = datetime(2023, 10, 9, 23, 59, 59) 
satellites = [Satellite('SOSO-1',(time_window_start,time_window_end)),
              Satellite('SOSO-2',(time_window_start,time_window_end)),
              Satellite('SOSO-3',(time_window_start,time_window_end)),
              Satellite('SOSO-4',(time_window_start,time_window_end)),
              Satellite('SOSO-5',(time_window_start,time_window_end))]

############################### process maintenance acticvities ############################### 
maintenance_path = "/app/order_samples/group1" # group 1 is a set of maintenance activities
maintenance_json_files = read_directory(maintenance_path)
print(f'{maintenance_path} contains {len(maintenance_json_files)} files.')

maintenance_activities = []
index = 1 # for the task ID
for json_file in maintenance_json_files:
    file_path = os.path.join(maintenance_path, json_file)
    with open(file_path, 'r') as file:
        data = json.load(file)
        # for simplicity, we only consider the window (start and end time) and duration 
        name = data["Activity"] + str(index)
        target = get_satellite_by_name(satellites, data["Target"])
        start_time = convert_str_to_datetime(data["Window"]["Start"])
        end_time = convert_str_to_datetime(data["Window"]["End"])
        duration = dt.timedelta(seconds=int(data["Duration"]))
        # print(f'activity name: {name}, start time: {start_time}, end time: {end_time}, duration: {duration}')
        # create a task object, with priority of 4, assuming that maintenance activities have the highest priority (higher than any imaging task)
        maintenance_activities.append(Task(name,start_time=start_time, end_time=end_time, duration=duration, priority=4, satellite=target))
    index += 1
print(f'There are {len(maintenance_activities)} maintenance activities.')

############################### process imaging tasks ###############################
imaging_path = "/app/order_samples/group2" # group 2 is a set of imaging tasks
imaging_json_files = read_directory(imaging_path)
print(f'{imaging_path} contains {len(imaging_json_files)} files.')

imaging_tasks = []
index = 1 # for the task ID
for json_file in imaging_json_files:
    file_path = os.path.join(imaging_path, json_file)
    with open(file_path, 'r') as file:
        # print(file_path)
        data = json.load(file)
        # for simplicity, we only consider the priority, window (start and end time) and duration 
        name = "ImagingTask" + str(index)
        priority = data["Priority"]
        start_time = convert_str_to_datetime(data["ImageStartTime"])
        end_time = convert_str_to_datetime(data["ImageEndTime"])
        image_type = get_image_type(data["ImageType"])
        duration = dt.timedelta(seconds=int(image_type.value['time_for_writing']))
        # print(f'activity name: {name}, start time: {start_time}, end time: {end_time}, duration: {duration}, priority: {priority}')
        # create a task object, with priority of 4, assuming that maintenance activities have the highest priority (higher than any imaging task)
        imaging_tasks.append(ImageTask(image_type=image_type, name=name,start_time=start_time, end_time=end_time, duration=duration, priority=priority))
    index += 1
print(f'There are {len(imaging_tasks)} Imaging tasks.')

############################################# Filter Imaging tasks ############################################################
from skyfield.api import Topos, load


def is_point_inside_box(latitude, longitude, box):
    min_lat, max_lat, min_lon, max_lon = box
    return min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon

def compute_time_window(observer, satellite, area_center, area_size_km, duration_hours, min_elevation_degrees):
    # Convert area size to degrees
    area_size_degrees = area_size_km / 111.32  # Approximate conversion for latitude

    # Define bounding box for the specified area
    area_box = (
        area_center[0] - area_size_degrees/2,
        area_center[0] + area_size_degrees/2,
        area_center[1] - area_size_degrees/2,
        area_center[1] + area_size_degrees/2
    )

    # Find passes over the bounding box
    t0 = load.timescale().now()
    t1 = t0.utc + duration_hours / 24.0
    passes = observer.find_events(satellite, t0, t1, altitude_degrees=0.0)

    # Check each pass for visibility, proper position, and minimum elevation angle
    for pass_event in passes:
        elevation = pass_event.altaz()[1].degrees  # Get elevation angle
        if (
            is_point_inside_box(pass_event.position().latitude().degrees, area_box[:2]) and
            is_point_inside_box(pass_event.position().longitude().degrees, area_box[2:]) and
            elevation > min_elevation_degrees
        ):
            start_time = pass_event.utc_iso()
            end_time = pass_event.utc_iso() + pass_event.duration
            print(f"Image capture window: Start: {start_time}, End: {end_time}, Duration: {pass_event.duration}, Elevation: {elevation} degrees")
            return

    print("No suitable time window found within the specified duration and minimum elevation.")

# Load satellite data (TLE - Two-Line Element set)
satellite_data = """ISS (ZARYA)
1 25544U 98067A   21250.82428147  .00002263  00000-0  50345-4 0  9999
2 25544  51.6468 317.7035 0006682 158.2955  14.7495 15.50454219307404
"""

# Define the observer's location (a point within the area, e.g., center)
observer_location = Topos(latitude_degrees=40.5, longitude_degrees=-74.5)

# Load the satellite and the observer location
ts = load.timescale()
satellite = load.tle_file_text(satellite_data)
observer = satellite['ISS'].at(observer_location)

# Define the area center and size
area_center = (40.7128, -74.0060)  # Latitude and Longitude of the area center (e.g., New York City)
area_size_km = 20.0  # Size of the area to capture in kilometers
duration_hours = 24.0  # Maximum duration to search for a suitable time window in hours
min_elevation_degrees = 60.0  # Minimum elevation angle for the pass

# Compute the time window for capturing the image
compute_time_window(observer, satellite, area_center, area_size_km, duration_hours, min_elevation_degrees)


print('----------------- SCHEDULING START -----------------')