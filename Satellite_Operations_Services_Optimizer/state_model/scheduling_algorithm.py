import json
import os
from datetime import datetime
import datetime as dt
from enum import Enum
from skyfield.api import EarthSatellite, load, Topos, utc
import math
from geopy.distance import geodesic

# satellite constants
SATELLITE_FULL_VIEW_ANGLE = 60
STORAGE_CAPACITY = 32 * 1024 # GB
# Image types constants
HIGH_WRITING_TIME = 120
HIGH_SIZE = 512 # MB
HIGH_DIMENSION = [10,10]
MEDIUM_WRITING_TIME = 45
MEDIUM_SIZE = 256 # MB
MEDIUM_DIMENSION = [40,20]
LOW_WRITING_TIME = 20
LOW_SIZE = 128 # MB
LOW_DIMENSION = [40,20]
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
    def __init__(self, name, activity_window, tle):
        self.name = name
        self.activity_window = activity_window
        self.schedule = [] # list of ((task_object, actual_start_time, real_end_time))
        self.tle = tle
        self.capacity = STORAGE_CAPACITY
        self.capacity_used = 0 

class MaintenanceTask(Task):
    def __init__(self, name, start_time, end_time, duration, priority, satellite, min_gap = None, max_gap = None):
        super().__init__(name = name, start_time = start_time, end_time = end_time, duration = duration, priority = priority, satellite = satellite)
        self.next_maintenance = None
        self.min_gap = min_gap
        self.max_gap = max_gap

class ImageTask(Task):
    def __init__(self, image_type, latitude, longitude, name, start_time, end_time, duration, priority, satellite = None):
        super().__init__(name = name, start_time = start_time, end_time = end_time, duration = duration, priority = priority, satellite = satellite)
        self.image_type = image_type
        self.latitude = latitude
        self.longitude = longitude

class ImageType(Enum):
    HIGH = {'time_for_writing':HIGH_WRITING_TIME, 'size':HIGH_SIZE, 'dimension':HIGH_DIMENSION}
    MEDIUM = {'time_for_writing':MEDIUM_WRITING_TIME, 'size':MEDIUM_SIZE, 'dimension':MEDIUM_DIMENSION}
    LOW = {'time_for_writing':LOW_WRITING_TIME, 'size':LOW_SIZE, 'dimension':LOW_DIMENSION}



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
        case "High":
            return ImageType.HIGH
        
def get_satellite_by_name(satellites, name):
    for satellite in satellites:
        if satellite.name == name:
            return satellite
    return None


def find_four_corner_coor(imaging_task):
    '''Given an imaging task (containing info of coordinates of imaging center, and image size),
    output the coordinates of the four corners of the image.'''
    # Calculate half-length and half-width
    half_length = imaging_task.image_type.value['dimension'][0] / 2
    half_width = imaging_task.image_type.value['dimension'][1] / 2

    # Extract latitude and longitude of the center
    center_lat, center_lon = imaging_task.latitude, imaging_task.longitude

    distance = math.sqrt(half_width**2+half_length**2)
    angle = math.degrees(math.atan(half_width/half_length))
    # print(distance, -angle, angle, angle-180, 180-angle)

    # Calculate the coordinates of the four corners
    top_left = geodesic(kilometers=distance).destination(point=(center_lat, center_lon), bearing=-angle) # top left
    top_right = geodesic(kilometers=distance).destination(point=(center_lat, center_lon), bearing=angle) # top right
    bottom_left = geodesic(kilometers=distance).destination(point=(center_lat, center_lon), bearing=angle-180) # bottom left
    bottom_right = geodesic(kilometers=distance).destination(point=(center_lat, center_lon), bearing=180-angle) # bottom right

    # Return the coordinates of the four corners
    # print(top_left.latitude, top_left.longitude) # top_left is a geodesic object
    return top_left, top_right, bottom_left, bottom_right

def get_time_window(satellite, point_on_earth, start_time, end_time, altitude_degree):
    """
    This method returns a list of time windows where each time windows includes time for : [acquisition of signal,
    loss of signal]

    @param satellite: a satellite created using define_satelite(TLE)
    @param groundstation: a ground station created using define_groundstation
    @param start_time: start time using load.timescale().utc()
    @param end_time: end time using load.timescale().utc()
    @param altitude_degree: a float number indicates the altitude degree
    @return: a list of time windows(list)
    """
    time_windows = []
    time, events = satellite.find_events(point_on_earth, start_time, end_time, altitude_degrees=altitude_degree)
    # print("!!!!!")
    # print(time, events)
    index = 0
    window = [None] * 2
    for t, e in zip(time, events):
        if index == 0:
            if e != 0:
                window[0] = start_time.utc_strftime('%Y %b %d %H:%M:%S')
            else:
                window[0] = t.utc_strftime('%Y %b %d %H:%M:%S')
            if e == 2:
                window[1] = t.utc_strftime('%Y %b %d %H:%M:%S')
                time_windows.append(list(window))
        elif index == len(time):
            if e != 2:
                window[1] = end_time.utc_strftime('%Y %b %d %H:%M:%S')
                time_windows.append(list(window))
        else:
            if e == 0:
                window[0] = t.utc_strftime('%Y %b %d %H:%M:%S')
            elif e == 2:
                window[1] = t.utc_strftime('%Y %b %d %H:%M:%S')
                time_windows.append(list(window))
        index += 1
    return time_windows


def find_satellite_achievability_of_point(satellite, imaging_task, latitude, longitude):
    '''Given a satellite, an imaging task, and the coordinates of a point on the Earth, 
    output the timeslots between the start time and end time of the task when this point is in the field of view of the satellite.'''
    point_on_earth = Topos(latitude_degrees=latitude, longitude_degrees=longitude, elevation_m=0)
    defined_satellite = EarthSatellite(satellite.tle[0], satellite.tle[1], satellite.name)
    ts = load.timescale()
    st = ts.utc(imaging_task.start_time.year, imaging_task.start_time.month, imaging_task.start_time.day, imaging_task.start_time.hour, imaging_task.start_time.minute, imaging_task.start_time.second)
    et = ts.utc(imaging_task.end_time.year, imaging_task.end_time.month, imaging_task.end_time.day, imaging_task.end_time.hour, imaging_task.end_time.minute, imaging_task.end_time.second)
    # print(st, et)
    time_windows = get_time_window(defined_satellite, point_on_earth, st, et, 90-SATELLITE_FULL_VIEW_ANGLE/2)

    for i,(start_time,end_time) in enumerate(time_windows):
        time_windows[i][0] = datetime.strptime(start_time, "%Y %b %d %H:%M:%S")
        time_windows[i][1] = datetime.strptime(end_time, "%Y %b %d %H:%M:%S")
    return time_windows

def check_overlap(timeslot1, timeslot2):
    early_et = None, None # start time and end time of the task that begins first
    late_st, late_et = None, None, # start time and end time of the task that begins later
    if timeslot1[0] <= timeslot2[0]: # task 1 begins first
        early_et = timeslot1[1]
        late_st, late_et = timeslot2[0], timeslot2[1]
    else: # task 2 begins first
        early_et = timeslot2[1]
        late_st, late_et = timeslot1[0], timeslot1[1]
    
    # find overlaps
    if late_st >= early_et: # the later task begins completely after the earlier task
        return None # no overlapping
    if early_et <= late_et: # the task that begins first also ends first
        return (late_st, early_et)
    else: # the task that begins first ends after the task that begins late
        return (late_st, late_et)



def find_common_achievability(achievability_lists):
    '''Given the list of satellite achievability of four corners of an image, 
    output the timeslots when all four corners are in the field of view of the satellite.'''
    common_achievabilities = []
    for x in achievability_lists[0]:
        for y in achievability_lists[1]:
            overlap12 = check_overlap(x,y)
            if overlap12:
                for u in achievability_lists[2]:
                    overlap123 = check_overlap(overlap12, u)
                    if overlap123:
                        for v in achievability_lists[3]:
                            overlap1234 = check_overlap(overlap123, v)
                            if overlap1234:
                                common_achievabilities.append(overlap1234)
    return common_achievabilities

def find_satellite_achievabilities(satellite, imaging_task):
    '''Given a satellite and an imaging task, 
    output the timeslots when the imaging area is in the field of view of the satellite.'''
    four_corners = find_four_corner_coor(imaging_task) # return a tuple of 4 geodesic objects 
    achievability_lists = []
    for corner in four_corners:
        # print(f"corner coordinates: {corner.latitude}, {corner.longitude}")
        achievability_lists.append(find_satellite_achievability_of_point(satellite, imaging_task, corner.latitude, corner.longitude)) # append timeslots of a corner
    common_achievabilities = find_common_achievability(achievability_lists)
    # print(common_achievabilities)
    return common_achievabilities


def initialize_satellites_tasks():
    ############################### Initialize satellites group 1 ################################
    # for TLE 1
    # with open('/app/TLE/tle1/SOSO-1_TLE.txt', 'r') as file: tle1 = file.read().split('\n')
    # with open('/app/TLE/tle1/SOSO-2_TLE.txt', 'r') as file: tle2 = file.read().split('\n')
    # with open('/app/TLE/tle1/SOSO-3_TLE.txt', 'r') as file: tle3 = file.read().split('\n')
    # with open('/app/TLE/tle1/SOSO-4_TLE.txt', 'r') as file: tle4 = file.read().split('\n')
    # with open('/app/TLE/tle1/SOSO-5_TLE.txt', 'r') as file: tle5 = file.read().split('\n')

    # for TLE 2
    # with open('/app/TLE/tle2/SOSO-6_TLE.txt', 'r') as file: tle1 = file.read().split('\n')
    # with open('/app/TLE/tle2/SOSO-7_TLE.txt', 'r') as file: tle2 = file.read().split('\n')
    # with open('/app/TLE/tle2/SOSO-8_TLE.txt', 'r') as file: tle3 = file.read().split('\n')
    # with open('/app/TLE/tle2/SOSO-9_TLE.txt', 'r') as file: tle4 = file.read().split('\n')
    # with open('/app/TLE/tle2/SOSO-10_TLE.txt', 'r') as file: tle5 = file.read().split('\n')

    # for TLE 3
    with open('/app/TLE/tle3/SOSO-1_TLE.txt', 'r') as file: tle1 = file.read().split('\n')
    with open('/app/TLE/tle3/SOSO-2_TLE.txt', 'r') as file: tle2 = file.read().split('\n')
    with open('/app/TLE/tle3/SOSO-3_TLE.txt', 'r') as file: tle3 = file.read().split('\n')
    with open('/app/TLE/tle3/SOSO-4_TLE.txt', 'r') as file: tle4 = file.read().split('\n')
    with open('/app/TLE/tle3/SOSO-5_TLE.txt', 'r') as file: tle5 = file.read().split('\n')

    time_window_start = datetime(2023, 10, 8, 00, 00, 00)
    time_window_end = datetime(2023, 10, 9, 23, 59, 59) 

    satellites1 = [Satellite('SOSO-1',(time_window_start,time_window_end), tle1),
                Satellite('SOSO-2',(time_window_start,time_window_end), tle2),
                Satellite('SOSO-3',(time_window_start,time_window_end), tle3),
                Satellite('SOSO-4',(time_window_start,time_window_end), tle4),
                Satellite('SOSO-5',(time_window_start,time_window_end), tle5)]

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
            target = get_satellite_by_name(satellites1, data["Target"])
            start_time = convert_str_to_datetime(data["Window"]["Start"])
            end_time = convert_str_to_datetime(data["Window"]["End"])
            duration = dt.timedelta(seconds=int(data["Duration"]))
            # revisit frequency
            num_repetition = data["RepeatCycle"]["Repetition"] 
            if num_repetition == "Null":
                maintenance_activities.append(MaintenanceTask(name, start_time, end_time, duration, 4, target))
            else:
                min_gap = data["RepeatCycle"]["Frequency"]["MinimumGap"]
                max_gap = data["RepeatCycle"]["Frequency"]["MaximumGap"]
                construct_and_add_revisit_maintenance_tasks(maintenance_activities, int(num_repetition), min_gap, max_gap, name, start_time, end_time, duration, target)
        index += 1
    print(f'There are {len(maintenance_activities)} maintenance activities.')




    ############################### Initialize satellites group 2 ################################
    # for group 2 images
    # time_window_start = datetime(2023, 11, 18, 00, 00, 00)
    # time_window_end = datetime(2023, 11, 18, 23, 59, 59) 

    # for group 3 old images
    # time_window_start = datetime(2023, 10, 8, 00, 00, 00)
    # time_window_end = datetime(2023, 10, 9, 23, 59, 59) 

    # for group 4 new images
    time_window_start = datetime(2023, 10, 2, 00, 00, 00)
    time_window_end = datetime(2023, 10, 2, 23, 59, 59) 

    satellites2 = [Satellite('SOSO-1',(time_window_start,time_window_end), tle1),
                Satellite('SOSO-2',(time_window_start,time_window_end), tle2),
                Satellite('SOSO-3',(time_window_start,time_window_end), tle3),
                Satellite('SOSO-4',(time_window_start,time_window_end), tle4),
                Satellite('SOSO-5',(time_window_start,time_window_end), tle5)]

    ############################### process imaging tasks ###############################
    imaging_path = "/app/order_samples/group4_newest" # group 2 is a set of imaging tasks
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
            lat = data["Latitude"]
            lon = data["Longitude"]
            # revisit frequency
            recurrence = data["Recurrence"]["Revisit"] 
            if recurrence == "False":
                define_and_add_imagaing_task(imaging_tasks, satellites2, image_type, lat, lon, name, start_time, end_time, duration, priority)
            elif recurrence == "True":
                num_revisit = int(data["Recurrence"]["NumberOfRevisits"])
                revisit_frequency = data["Recurrence"]["RevisitFrequency"]
                frequency_unit = data["Recurrence"]["RevisitFrequencyUnits"]
                define_and_add_imagaing_task(imaging_tasks, satellites2, image_type, lat, lon, name, start_time, end_time, duration, priority)
                construct_and_add_revisit_imaging_tasks(num_revisit-1, revisit_frequency, frequency_unit, imaging_tasks, satellites2, image_type, lat, lon, name, start_time, end_time, duration, priority)
        index += 1
    print(f'There are {len(imaging_tasks)} Imaging tasks.')

    return satellites1, satellites2, maintenance_activities, imaging_tasks

def construct_and_add_revisit_imaging_tasks(num_revisit, revisit_frequency, frequency_unit, imaging_tasks, satellites2, image_type, lat, lon, name, start_time, end_time, duration, priority):
    for r in range(num_revisit):
        next_name = name + "Revisit" + str(r+1)
        if frequency_unit == "Hours":
            next_start_time = start_time + dt.timedelta(hours=int(r*revisit_frequency))
            next_end_time = end_time + dt.timedelta(hours=int(r*revisit_frequency))
            define_and_add_imagaing_task(imaging_tasks, satellites2, image_type, lat, lon, next_name, next_start_time, next_end_time, duration, priority)
        elif frequency_unit == "Days":
            next_start_time = start_time + dt.timedelta(days=int(r*revisit_frequency))
            next_end_time = end_time + dt.timedelta(days=int(r*revisit_frequency))
            define_and_add_imagaing_task(imaging_tasks, satellites2, image_type, lat, lon, next_name, next_start_time, next_end_time, duration, priority)


def define_and_add_imagaing_task(imaging_tasks, satellites2, image_type, lat, lon, name, start_time, end_time, duration, priority):
    new_imaging_task = ImageTask(image_type=image_type, latitude=lat, longitude=lon, name=name,start_time=start_time, end_time=end_time, duration=duration, priority=priority)
    # find satellites find_satellite_achievabilities for this imaging task
    achievabilities = {}
    for s in satellites2:
        achievabilities[s] = find_satellite_achievabilities(s,new_imaging_task)
    new_imaging_task.achievability = achievabilities
    imaging_tasks.append(new_imaging_task)

def construct_and_add_revisit_maintenance_tasks(maintenance_activities, num_repetition, min_gap, max_gap, name, start_time, end_time, duration, target):
    previous_task = MaintenanceTask(name, start_time, end_time, duration, 4, target, min_gap, max_gap)
    maintenance_activities.append(previous_task)
    for r in range(int(num_repetition)-1):
        next_name = name + "Revisit" + str(r+1)
        next_task = MaintenanceTask(next_name, None, None, duration, 4, target, min_gap, max_gap) # not able to decide the activity window until the the first time has been scheduled
        previous_task.next_maintenance = next_task
        previous_task = next_task


# print("PRINT TASKS: ")
# _,_,maintenances,_ = initialize_satellites_tasks()
# for task in maintenances:
#     print(task.name, task.start_time, task.end_time)
# print('---------------------------------------------')

# print(type(imaging_tasks[2].achievability['SOSO-1'][0][0]))
# print(imaging_tasks[2].achievability['SOSO-1'][0][0])