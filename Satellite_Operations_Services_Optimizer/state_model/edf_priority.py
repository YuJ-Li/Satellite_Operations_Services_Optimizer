# from .repositories import *
import json
import os
from datetime import datetime
import datetime as dt
from enum import Enum
from skyfield.api import EarthSatellite, load, wgs84, Topos
import math


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
        self.schedule = [] # list of ((#task_name, actual_start_time, real_end_time))
        self.tle = tle


class ImageTask(Task):
    def __init__(self, image_type, latitude, longitude, name, start_time, end_time, duration, priority, satellite = None):
        super().__init__(name = name, start_time = start_time, end_time = end_time, duration = duration, priority = priority, satellite = satellite)
        self.image_type = image_type
        self.latitude = latitude
        self.longitude = longitude

class ImageType(Enum):
    SPOTLIGHT = {'time_for_writing':120, 'size':512, 'dimension':[10,10]}
    MEDIUM = {'time_for_writing':45, 'size':256, 'dimension':[40,20]}
    LOW = {'time_for_writing':20, 'size':128, 'dimension':[40,20]}


##################################### EDF functions ######################################
def group_by_priority(task_list):
    priority_list = {}
    for task in task_list:
        if priority_list.get(task.priority) is None:
            priority_list[task.priority] = [task]
        else:
            priority_list[task.priority].append(task)
    priority_list = dict(sorted(priority_list.items(), key=lambda item: item[0], reverse=True))
    return priority_list

def print_priority_list(priority_list):
    for p_group in priority_list.items():
        s = str(p_group[0]) + ": "
        for t in p_group[1]:
            s = s + t.name + ", "
        print(s)


def edf(priority_list, satellites):
    ''' priority_tasks is a dictionary of tasks grouped by priority'''
    unscheduled_tasks = []
    # sorts tasks in each priority group by deadline
    for p_group in priority_list.items(): 
        tasks = p_group[1]
        tasks.sort(key=lambda x: (x.end_time,x.start_time)) # for each priority group, sort tasks by end time then by start time
        s = str(p_group[0]) + ": "
        for t in tasks:
            s = s + t.name + ", "
        for task in tasks:
            scheduled = False
            for satellite in satellites:
                # TODO: check if the task is achievable on this satellite
                if task.satellite is not None and task.satellite != satellite: continue
                schedule_ptr = -1
                while not scheduled and schedule_ptr<len(satellite.schedule):
                    empty_slot_start, empty_slot_end, schedule_ptr = find_next_slot(satellite, schedule_ptr)
                    if empty_slot_start is not None and empty_slot_end is not None:
                        if task.start_time < empty_slot_start and empty_slot_start + task.duration <= empty_slot_end and empty_slot_start + task.duration <= task.end_time:
                            scheduled_start = empty_slot_start
                            scheduled_end = scheduled_start + task.duration
                            satellite.schedule.insert(schedule_ptr, (task.name, scheduled_start, scheduled_end)) 
                            scheduled = True
                            # print(f'{task.name} is scheduled on {satellite.name}.')
                            break
                        elif task.start_time >= empty_slot_start and task.start_time + task.duration <= empty_slot_end and task.start_time + task.duration <= task.end_time:
                            scheduled_start = task.start_time
                            scheduled_end = scheduled_start + task.duration
                            satellite.schedule.insert(schedule_ptr, (task.name, scheduled_start, scheduled_end)) 
                            scheduled = True
                            # print(f'{task.name} is scheduled on {satellite.name}.')
                            break
                if scheduled: break
            if not scheduled:
                unscheduled_tasks.append(task)
                # print(f'Failed to schedule {task.name}.')
            else:
                # if a task got scheduled, re-sort the satellites by increasing number of tasks scheduled on them
                # to ensure satellite
                satellites = sort_satellites_by_number_of_tasks(satellites)

    print(f'{len(unscheduled_tasks)} tasks failed to be scheduled: ')
    for t in unscheduled_tasks:
        print(t.name)
    

def find_next_slot(satellite, ptr):
    '''ptr is the index of task scheduled on this satellite from which we start to find empty slot'''
    satellite_schedule = satellite.schedule
    if len(satellite_schedule)==0: 
        return satellite.activity_window[0], satellite.activity_window[1], 0 # if nothing has been scheduled on the satellite yet, return the entire availility of the satellite
    if ptr == -1: # if pointer is pointing at the beginning of the schedule
        if satellite_schedule[0][1] - satellite.activity_window[0] > dt.timedelta(seconds=0): # if there is space between the start of activity window and the start of first task
            return satellite.activity_window[0], satellite_schedule[0][1], ptr+1
        ptr += 1
    for i in range(ptr, len(satellite_schedule)-1):
        if satellite_schedule[i+1][1] - satellite_schedule[i][2] > dt.timedelta(seconds=0): # if there is time between the start of next task and the end of this task
            return satellite_schedule[i][2],satellite_schedule[i+1][1], i+1
        ptr += 1
    if ptr == len(satellite_schedule)-1:
        if satellite.activity_window[1] - satellite_schedule[ptr][2] > dt.timedelta(seconds=0):
            return satellite_schedule[ptr][2], satellite.activity_window[1], ptr+1
    return None, None, ptr+1


def sort_satellites_by_number_of_tasks(satellites):
    sorted_satellites = sorted(satellites, key=lambda x: len(x.schedule))
    return sorted_satellites


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


#####################################################################################
#####################################################################################

def check_task_achievability_on_satellite(imaging_tasks, satellites):
    achievabilities = []
    for task in imaging_tasks:
        satellite_achievabilities = {}
        for satellite in satellites:
            tle_satellite = EarthSatellite(satellite.tle[1], satellite.tle[2], satellite.name)

            center_lat = task.latitude
            center_lon = task.longitude
            image_corner1,image_corner2,image_corner3,image_corner4 = find_corner_lat_lon(center_lat, center_lon, task.value["dimension"])

            # time1, events1 = tle_satellite.find_events(image_corner1, task.start_time, task.end_time, altitude_degrees=60)
            # time2, events2 = tle_satellite.find_events(image_corner2, task.start_time, task.end_time, altitude_degrees=60)
            # time3, events3 = tle_satellite.find_events(image_corner3, task.start_time, task.end_time, altitude_degrees=60)
            # time4, events4 = tle_satellite.find_events(image_corner4, task.start_time, task.end_time, altitude_degrees=60)

            # for t, e in zip(time, events):
    return achievabilities
    

def find_corner_lat_lon(center_lat, center_lon, dimension):
    # https://en.wikipedia.org/wiki/Latitude
    # N,E:+
    # S,W:-
    # Longitude: km divided by 111.320 
    corner_east = longitude_normalization(center_lon + (dimension[1]/2)/111.320)
    corner_west = longitude_normalization(center_lon - (dimension[1]/2)/111.320)
    # Latitude: km divided by 110.574 
    corner_north = center_lat + (dimension[0]/2)/110.574 
    corner_south = center_lat - (dimension[0]/2)/110.574
    if corner_north>90:
        corner_north = 90-(corner_north-90)
        # flip longtitude
        corner_east2 = longitude_normalization(corner_east + 180)
        corner_west2 = longitude_normalization(corner_west + 180)
        # return corners (north-east, north-west, south-east, south-west)
        return [(corner_north, corner_east2),(corner_north, corner_west2),(corner_south, corner_east),(corner_south, corner_west)]
    if corner_south<-90:
        corner_south = -90 - (corner_south + 90)
        # flip longitude
        corner_east2 = longitude_normalization(corner_east + 180)
        corner_west2 = longitude_normalization(corner_west + 180)
        # return corners (north-east, north-west, south-east, south-west)   
        return [(corner_north, corner_east),(corner_north, corner_west),(corner_south, corner_east2),(corner_south, corner_west2)]
    return [(corner_north, corner_east),(corner_north, corner_west),(corner_south, corner_east),(corner_south, corner_west)]


def longitude_normalization(degree):
    if degree > 180:
        return degree % 180 - 180
    elif degree < -180:
        return 180 - abs(degree) % 180
    else: 
        return degree





############################### Initialize satellites ################################
with open('/app/TLE/SOSO-1_TLE.txt', 'r') as file: tle1 = file.read()
with open('/app/TLE/SOSO-2_TLE.txt', 'r') as file: tle2 = file.read()
with open('/app/TLE/SOSO-3_TLE.txt', 'r') as file: tle3 = file.read()
with open('/app/TLE/SOSO-4_TLE.txt', 'r') as file: tle4 = file.read()
with open('/app/TLE/SOSO-5_TLE.txt', 'r') as file: tle5 = file.read()

time_window_start = datetime(2023, 10, 8, 00, 00, 00)
time_window_end = datetime(2023, 10, 9, 23, 59, 59) 

satellites = [Satellite('SOSO-1',(time_window_start,time_window_end), tle1),
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
        lat = data["Latitude"]
        lon = data["Longitude"]
        # print(f'activity name: {name}, start time: {start_time}, end time: {end_time}, duration: {duration}, priority: {priority}')
        # create a task object, with priority of 4, assuming that maintenance activities have the highest priority (higher than any imaging task)
        imaging_tasks.append(ImageTask(image_type=image_type, latitude=lat, longitude=lon, name=name,start_time=start_time, end_time=end_time, duration=duration, priority=priority))
    index += 1
print(f'There are {len(imaging_tasks)} Imaging tasks.')



print('----------------- SCHEDULING START -----------------')

# TODO 1: use your scheduling algorithm to schedule tasks in `maintenance_activities` on the five satellites
# priority_list = group_by_priority(maintenance_activities)

# # print_priority_list(priority_list)

# edf(priority_list, satellites)

# print('------------------')
# for satellite in satellites:
#     print(satellite.name, ':')
#     for t in satellite.schedule:
#         print(t[0])

# TODO 2: use your scheduling algorithm to schedule tasks in `imaging_tasks` on the five satellites
# priority_list = group_by_priority(imaging_tasks)

# # print_priority_list(priority_list)

# edf(priority_list, satellites)

# print('------------------')
# for satellite in satellites:
#     print(satellite.name, ':')
#     for t in satellite.schedule:
#         print(t[0])

# TODO 3: use your scheduling algorithm to schedule tasks in BOTH lists on the five satellites
all_tasks = imaging_tasks
all_tasks.extend(maintenance_activities)
priority_list = group_by_priority(all_tasks)

# print_priority_list(priority_list)

edf(priority_list, satellites)

print('------------------')
for satellite in satellites:
    print(satellite.name, ':')
    for t in satellite.schedule:
        print(t[0])
 





# check satellite availibility (fov)
# target satellite !
# all satellites start and end at the same time !
# distribution equally !
