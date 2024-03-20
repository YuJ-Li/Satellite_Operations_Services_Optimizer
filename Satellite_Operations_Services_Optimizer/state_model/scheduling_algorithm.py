import json
import os
from datetime import datetime
import datetime as dt
from enum import Enum
from skyfield.api import EarthSatellite, load, Topos, utc
import math
from geopy.distance import geodesic
from datetime import timezone
import copy
import glob
from .models import Satellite, ImageTask, MaintenanceTask, GroundStation, GroundStationRequest, Outage, SatelliteTask
# from edf_priority import *

# # satellite constants
SATELLITE_FULL_VIEW_ANGLE = 60
STORAGE_CAPACITY = 32.0 * 1024.0 # GB
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


ACCUMULATED_IMAGING_TASKS = {} # a priority dictionary
ACCUMULATED_MAINTENANCE_TASKS = {} # a priority dictionary
IMAGING_TASK_HISTORY = []
MAINTENANCE_TASK_HISTORY = []
SATELLITES = []
GLOBAL_TIME = datetime.now(timezone.utc)
ACTIVITY_WINDOW = (GLOBAL_TIME, GLOBAL_TIME + dt.timedelta(hours=2))
###################################### CLASSES ###########################################

# class Task:
#     def __init__(self, name, start_time, end_time, duration, priority, satellite = None):
#         self.name = name
#         self.start_time = start_time
#         self.end_time = end_time
#         self.duration = duration
#         self.priority = priority # imaging tasks: priority from 3 to 1 = from high to low; maintenance activity: priority = 4 (highest)
#         self.satellite = satellite # to be determined by the scheduling algorithm

# class Satellite:
#     def __init__(self, name, tle):
#         self.name = name
#         # self.ACTIVITY_WINDOW = ACTIVITY_WINDOW
#         self.schedule = [] # list of ((task_object, actual_start_time, real_end_time))
#         self.maintenance_without_outage = []  # list of ((maintenance_activity, actual_start_time, real_end_time)) that does not cause payload outage
#         self.tle = tle
#         self.capacity = STORAGE_CAPACITY
#         self.capacity_used = 0 

# class MaintenanceTask(Task):
#     def __init__(self, name, start_time, end_time, duration, priority, satellite, payload_outage, min_gap = None, max_gap = None):
#         super().__init__(name = name, start_time = start_time, end_time = end_time, duration = duration, priority = priority, satellite = satellite)
#         self.next_maintenance = None
#         self.is_head = False
#         self.min_gap = min_gap
#         self.max_gap = max_gap
#         self.payload_outage = payload_outage

# class ImageTask(Task):
#     def __init__(self, image_type, latitude, longitude, name, start_time, end_time, duration, priority, satellite = None):
#         super().__init__(name = name, start_time = start_time, end_time = end_time, duration = duration, priority = priority, satellite = satellite)
#         self.image_type = image_type
#         self.latitude = latitude
#         self.longitude = longitude

# class ImageType(Enum):
#     HIGH = {'time_for_writing':HIGH_WRITING_TIME, 'size':HIGH_SIZE, 'dimension':HIGH_DIMENSION}
#     MEDIUM = {'time_for_writing':MEDIUM_WRITING_TIME, 'size':MEDIUM_SIZE, 'dimension':MEDIUM_DIMENSION}
#     LOW = {'time_for_writing':LOW_WRITING_TIME, 'size':LOW_SIZE, 'dimension':LOW_DIMENSION}


####################################### EDF Functions ###############################################
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


def edf_imaging(priority_list,satellites):
    ''' priority_tasks is a dictionary of tasks grouped by priority'''
    unscheduled_tasks = {} # to store un sc
    # sorts tasks in each priority group by deadline
    for p_group in priority_list.items(): 
        tasks = p_group[1]
        tasks.sort(key=lambda x: (x.end_time,x.start_time)) # for each priority group, sort tasks by end time then by start time
        for task in tasks:
            scheduled = False
            task_achi = json.loads(task.achievability)

            valid_keys = [get_satellite_by_name(satellites,key) for key, value in task_achi.items() if value != []] # list of satellites that can see this task in task's time window
            if valid_keys is None: # if this task is not in the FOV of any satellite within its available time window
                add_task_to_priority_list(unscheduled_tasks, task) # consider it as non schedulable
                continue 
            # sort the satellites by increasing number of tasks scheduled on them to ensure satellites are equally used
            valid_keys = sort_satellites_by_number_of_tasks(valid_keys)
            
            for satellite in valid_keys:
                # if task.satellite is not None and task.satellite != satellite: continue
                if satellite.capacity_used + get_image_type(task.image_type)['size'] > satellite.storage_capacity: continue
                schedule_ptr = -1
                satellite_schedule = json.loads(satellite.schedule)
                while not scheduled and schedule_ptr<len(satellite_schedule):
                    empty_slot_start, empty_slot_end, schedule_ptr = find_next_slot(satellite, schedule_ptr)
                    if not isinstance(empty_slot_start, datetime):
                        empty_slot_start = convert_str_to_datetime(empty_slot_start)
                    if not isinstance(empty_slot_end, datetime):
                        empty_slot_end = convert_str_to_datetime(empty_slot_end)
                    # print(f"for {task.name} on {satellite.name}: {empty_slot_start} -- {empty_slot_end}")
                    imaging_taking_time = check_imaging_task_can_fit_in_timeslot(empty_slot_start, empty_slot_end, task, task_achi[satellite.name])
                    if imaging_taking_time:
                        scheduled_start = imaging_taking_time
                        scheduled_end = scheduled_start + task.duration
                        satellite_schedule.insert(schedule_ptr, (task.name, convert_datetime_to_str(scheduled_start), convert_datetime_to_str(scheduled_end))) 
                        satellite.capacity_used += get_image_type(task.image_type)['size']
                        scheduled = True
                        # print(f'{task.name} is scheduled on {satellite.name}.')
                        break
                if scheduled: 
                    satellite.schedule = json.dumps(satellite_schedule)
                    break
            if not scheduled:
                add_task_to_priority_list(unscheduled_tasks, task)
    return unscheduled_tasks
    
def check_imaging_task_can_fit_in_timeslot(empty_slot_start, empty_slot_end, imaging_task, satellite_achievability):
    '''Given the start time and end time of an empty timeslot, check if the given imaging task can be fitted in the schedule of a satellite.
    @param satellite_achievability: the timeslots when the specific imaging area is in the FOV of the specific satellite
    Consider the duration of the task and the fact that taking the image (time required for the entire image to stay in the FOV) is one shot'''
    for (fov_st, fov_et) in satellite_achievability:
        fov_st, fov_et = convert_str_to_datetime(fov_st), convert_str_to_datetime(fov_et)
        if fov_st <= empty_slot_start and fov_et >= empty_slot_start:
            # image taking happens at empty_slot_start
            if empty_slot_start + imaging_task.duration <= empty_slot_end and empty_slot_start + imaging_task.duration <= imaging_task.end_time:
                return empty_slot_start
        elif fov_st > empty_slot_start and fov_et <= empty_slot_end:
            # image taking happens at fov_st
            if fov_st + imaging_task.duration <= empty_slot_end and fov_st + imaging_task.duration <= imaging_task.end_time:
                return fov_st
        else: 
            return None



def edf_maintenance(priority_list, satellites):
    ''' priority_tasks is a dictionary of tasks grouped by priority'''
    global ACCUMULATED_MAINTENANCE_TASKS 

    unscheduled_tasks = {}
    # sorts tasks in each priority group by deadline
    for p_group in priority_list.items(): 
        tasks = p_group[1]
        print(f'found {len(tasks)} tasks to schedule')
        # tasks.sort(key=lambda x: (x.end_time,x.start_time)) # for each priority group, sort tasks by end time then by start time
        for task in tasks:
            if task.is_head: 
                satellite = get_satellite_by_name(satellites, task.satellite.name)
                scheduled, scheduled_start = schedule_maintenance_task(task, satellite)
                if not scheduled:
                    print('cannot be scheduled')
                    add_task_to_priority_list(unscheduled_tasks, task)
                    # print(f'Failed to schedule {task.name}.')
                else:
                    print('to be scheduled')
                    # schedule the next revisit activity
                    while scheduled and len(task.next_maintenance)>0:
                        print('while loop: ', task.next_maintenance)
                        next_task = get_task_by_name_from_specific_list(task.next_maintenance, tasks)
                        next_task.start_time = scheduled_start + dt.timedelta(seconds=int(task.min_gap))
                        next_task.end_time = scheduled_start + dt.timedelta(seconds=int(task.max_gap)) + next_task.duration
                        scheduled, scheduled_start = schedule_maintenance_task(next_task, satellite)
                        task = next_task
                    print('while loop ends')
                    # if not scheduled:
                    #     add_task_to_priority_list(unscheduled_tasks, next_task) # if a revisit activity failed to be scheduled, add it to the pool of unscheduled for future consideration
                print('4.3')
    return unscheduled_tasks

def schedule_maintenance_task(task, satellite):
    scheduled = False
    scheduled_start = None
    schedule_ptr = -1
    satellite_schedule = json.loads(satellite.schedule)
    while not scheduled and schedule_ptr<len(satellite_schedule):
        empty_slot_start, empty_slot_end, schedule_ptr = find_next_slot(satellite, schedule_ptr)
        if empty_slot_start is not None and empty_slot_end is not None:
            if task.start_time < empty_slot_start and empty_slot_start + task.duration <= empty_slot_end and empty_slot_start + task.duration <= task.end_time:
                scheduled_start = empty_slot_start
                scheduled_end = scheduled_start + task.duration
                satellite_schedule.insert(schedule_ptr, (task.name, convert_datetime_to_str(scheduled_start), convert_datetime_to_str(scheduled_end))) 
                scheduled = True
                satellite.schedule = json.dumps(satellite_schedule)
                # print(f'{task.name} is scheduled on {satellite.name}.')
                break
            elif task.start_time >= empty_slot_start and task.start_time + task.duration <= empty_slot_end and task.start_time + task.duration <= task.end_time:
                scheduled_start = task.start_time
                scheduled_end = scheduled_start + task.duration
                satellite_schedule.insert(schedule_ptr, (task.name, convert_datetime_to_str(scheduled_start), convert_datetime_to_str(scheduled_end))) 
                scheduled = True
                satellite.schedule = json.dumps(satellite_schedule)
                # print(f'{task.name} is scheduled on {satellite.name}.')
                break 
    # if scheduled:
    #     satellite_schedule = json.loads(satellite.schedule)
    #     for t in satellite_schedule:
    #         print(f'SUCCESS!!!!!: {t[0]} : {t[1]} ---> {t[2]}')
    return scheduled,scheduled_start

def find_next_slot(satellite, ptr):
    '''ptr is the index of task scheduled on this satellite from which we start to find empty slot'''
    global ACTIVITY_WINDOW

    satellite_schedule = json.loads(satellite.schedule)
    if len(satellite_schedule)==0: 
        return ACTIVITY_WINDOW[0], ACTIVITY_WINDOW[1], 0 # if nothing has been scheduled on the satellite yet, return the entire availility of the satellite
    if ptr == -1: # if pointer is pointing at the beginning of the schedule
        if isinstance(get_task_by_name(satellite_schedule[0][0]), MaintenanceTask) and not get_task_by_name(satellite_schedule[0][0]).payload_outage: # if the first activity is a maintenance task and it does not affect payload
            if len(satellite_schedule)>1:
                return ACTIVITY_WINDOW[0], convert_str_to_datetime(satellite_schedule[1][1]), ptr+1 # available time slot lasts until the beginning of the next maintenance task
            else:
                return ACTIVITY_WINDOW[0], ACTIVITY_WINDOW[1], ptr+1
        elif convert_str_to_datetime(satellite_schedule[0][1]) - ACTIVITY_WINDOW[0] > dt.timedelta(seconds=0): # if there is space between the start of activity window and the start of first task
            return ACTIVITY_WINDOW[0], convert_str_to_datetime(satellite_schedule[0][1]), ptr+1
        ptr += 1
    for i in range(ptr, len(satellite_schedule)-1):
        # TODO: maintenance task without payload outage          
        if convert_str_to_datetime(satellite_schedule[i+1][1]) - convert_str_to_datetime(satellite_schedule[i][2]) > dt.timedelta(seconds=0): # if there is time between the start of next task and the end of this task
            return convert_str_to_datetime(satellite_schedule[i][2]),convert_str_to_datetime(satellite_schedule[i+1][1]), i+1
        ptr += 1
    if ptr == len(satellite_schedule)-1:
        # TODO: maintenance task without payload outage
        if ACTIVITY_WINDOW[1] - convert_str_to_datetime(satellite_schedule[ptr][2]) > dt.timedelta(seconds=0):
            return convert_str_to_datetime(satellite_schedule[ptr][2]), ACTIVITY_WINDOW[1], ptr+1
    return None, None, ptr+1


def sort_satellites_by_number_of_tasks(satellites):
    sorted_satellites = sorted(satellites, key=lambda x: len(json.dumps(x.schedule)))
    return sorted_satellites


######################################## General functions ##########################################

def read_directory(path):
    json_files = [f.path for f in os.scandir(path) if f.is_file() and f.name.endswith(('.json', '.JSON'))]
    return json_files

def convert_str_to_datetime(datetime_str):
    date_and_time = datetime_str.split('T')
    arr = date_and_time[0].split('-')
    arr.extend(date_and_time[1].split(':'))
    datetime_obj = datetime(int(arr[0]),int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]),int(arr[5]), tzinfo=timezone.utc)
    return datetime_obj

def get_image_type(image_type):
    match image_type:
        case "Low":
            return {'time_for_writing':LOW_WRITING_TIME, 'size':LOW_SIZE, 'dimension':LOW_DIMENSION}
            # return ImageTask.LOW
        case "Medium":
            return {'time_for_writing':MEDIUM_WRITING_TIME, 'size':MEDIUM_SIZE, 'dimension':MEDIUM_DIMENSION}
            # return ImageTask.MEDIUM
        case "High":
            return {'time_for_writing':HIGH_WRITING_TIME, 'size':HIGH_SIZE, 'dimension':HIGH_DIMENSION}
            # return ImageTask.HIGH
        
def get_satellite_by_name(satellites, name):
    for satellite in satellites:
        if satellite.name == name:
            return satellite
    return None

def get_task_by_name(name):
    global ACCUMULATED_IMAGING_TASKS
    global ACCUMULATED_MAINTENANCE_TASKS
    for prio in ACCUMULATED_IMAGING_TASKS:
        for task in ACCUMULATED_IMAGING_TASKS[prio]:
            if task.name == name: return task
    for prio in ACCUMULATED_MAINTENANCE_TASKS:
        for task in ACCUMULATED_MAINTENANCE_TASKS[prio]:
            if task.name == name: return task
    return None

def find_four_corner_coor(imaging_task):
    '''Given an imaging task (containing info of coordinates of imaging center, and image size),
    output the coordinates of the four corners of the image.'''
    # Calculate half-length and half-width
    half_length = get_image_type(imaging_task.image_type)['dimension'][0] / 2
    half_width = get_image_type(imaging_task.image_type)['dimension'][1] / 2

    # Extract latitude and longitude of the center
    center_lat, center_lon = imaging_task.imagingRegionLatitude, imaging_task.imagingRegionLongitude

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
        time_windows[i][0] = time_windows[i][0].replace(tzinfo=timezone.utc)
        time_windows[i][1] = datetime.strptime(end_time, "%Y %b %d %H:%M:%S")
        time_windows[i][1] = time_windows[i][1].replace(tzinfo=timezone.utc)
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
    # convert datetime objects in achievabilities to strings
    for i,(dt1, dt2) in enumerate(common_achievabilities):
        dt1 = convert_datetime_to_str(dt1)
        dt2 = convert_datetime_to_str(dt2)
        common_achievabilities[i] = (dt1, dt2)
    return common_achievabilities


def construct_and_add_revisit_imaging_tasks(num_revisit, revisit_frequency, frequency_unit, satellites2, image_type, lat, lon, name, start_time, end_time, duration, priority):
    task_list = []
    for r in range(1,num_revisit+1):
        next_name = name + "_Revisit_" + str(r)
        if frequency_unit == "Hours":
            next_start_time = start_time + dt.timedelta(hours=int(r*revisit_frequency))
            next_end_time = end_time + dt.timedelta(hours=int(r*revisit_frequency))
            new_task = define_and_add_imagaing_task(satellites2, image_type, lat, lon, next_name, next_start_time, next_end_time, duration, priority)
            task_list.append(new_task)
        elif frequency_unit == "Days":
            next_start_time = start_time + dt.timedelta(days=int(r*revisit_frequency))
            next_end_time = end_time + dt.timedelta(days=int(r*revisit_frequency))
            new_task = define_and_add_imagaing_task(satellites2, image_type, lat, lon, next_name, next_start_time, next_end_time, duration, priority)
            task_list.append(new_task)
    return task_list

def define_and_add_imagaing_task(satellites2, image_type, lat, lon, name, start_time, end_time, duration, priority):
    new_imaging_task = ImageTask(image_type=image_type, imagingRegionLatitude=lat, imagingRegionLongitude=lon, name=name,start_time=start_time, end_time=end_time, duration=duration, priority=priority, achievability=json.dumps({}))
    # find satellites find_satellite_achievabilities for this imaging task
    achievabilities = {}
    for s in satellites2:
        achievabilities[s.name] = find_satellite_achievabilities(s,new_imaging_task)
    new_imaging_task.achievability = json.dumps(achievabilities)
    # imaging_tasks.append(new_imaging_task)
    return new_imaging_task

def construct_and_add_revisit_maintenance_tasks(num_repetition, payload_outage, min_gap, max_gap, name, start_time, end_time, duration, target):
    tasks = []
    first_task = MaintenanceTask(name=name, 
                                 start_time=start_time, 
                                 end_time=end_time, 
                                 duration=duration, 
                                 priority=4, 
                                 satellite=target, 
                                 is_head=True,
                                 payload_outage=payload_outage, 
                                 min_gap=min_gap, 
                                 max_gap=max_gap
                                 )
    tasks.append(first_task)
    previous_task = first_task

    for r in range(int(num_repetition)):
        next_name = name + "_Revisit" + str(r+1)
        next_task = MaintenanceTask(name=next_name, 
                                    start_time=None, 
                                    end_time=None, 
                                    duration=duration, 
                                    priority=4, 
                                    satellite=target, 
                                    is_head=False,
                                    payload_outage=payload_outage, 
                                    min_gap=min_gap, 
                                    max_gap=max_gap
                                    ) # not able to decide the activity window until the the first time has been scheduled
        previous_task.next_maintenance = next_task.name
        previous_task = next_task
        tasks.append(next_task)
    return tasks



'''
input variable time: in format of "2024-02-06 15:30:00"
'''
def set_global_time(date_string):
    global GLOBAL_TIME
    global ACTIVITY_WINDOW
    # Convert the string to a datetime object
    datetime_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    datetime_utc0 = datetime_object.replace(tzinfo=timezone.utc)
 
    GLOBAL_TIME = datetime_utc0
    ACTIVITY_WINDOW = (GLOBAL_TIME, GLOBAL_TIME + dt.timedelta(days=2))
    return GLOBAL_TIME

def get_global_time():
    global GLOBAL_TIME
    return GLOBAL_TIME


# Trigger of adding new task
def add_new_imaging_task(satellites,task):
    global ACCUMULATED_IMAGING_TASKS
    # global SATELLITES
    global GLOBAL_TIME

    # clear expired tasks from the task lists
    clear_expired_tasks(ACCUMULATED_IMAGING_TASKS)

    # determine if the new tasks are potentially achievable according to the current time, if yes, add the new tasks to the pool 
    # for task in tasks:
    if task.end_time - task.duration > GLOBAL_TIME: # if the lastest start time is later than current time
        # then this task is potentially feasible, add it to the list
        if ACCUMULATED_IMAGING_TASKS.get(task.priority) is None:
            ACCUMULATED_IMAGING_TASKS[task.priority] = [task]
            ACCUMULATED_IMAGING_TASKS = dict(sorted(ACCUMULATED_IMAGING_TASKS.items(), key=lambda item: item[0], reverse=True))
        else:
            ACCUMULATED_IMAGING_TASKS[task.priority].append(task)
    
    # clear tasks that has been finished and that is being executed at current time
    update_imaging_pool()
        
    # do EDF
    ACCUMULATED_IMAGING_TASKS = edf_imaging(ACCUMULATED_IMAGING_TASKS, satellites)
    
    return 0

'''
Put all unexecuted imaging tasks back into the pool for future reschedule
'''
def update_imaging_pool():
    global ACCUMULATED_IMAGING_TASKS
    global SATELLITES
    global GLOBAL_TIME
    for s in SATELLITES:
        schedule = json.loads(s.schedule)
        tasks_to_remove = []
        for t in schedule:
            if isinstance(t[0], ImageTask): # if the imaging task has not been executed (hasn's started) yet
                process_image_task(tasks_to_remove, t)
        for task in tasks_to_remove:
            schedule.remove(task) 
            s.capacity_used -= get_image_type(task.image_type)['size']
        s.schedule = json.dumps(schedule)
    ACCUMULATED_IMAGING_TASKS = dict(sorted(ACCUMULATED_IMAGING_TASKS.items(), key=lambda item: item[0], reverse=True))

'''
Put all unexecuted maintenence and imaging tasks back into the pool for future reschedule
'''
def update_maintenenace_and_imaging_pool():
    global ACCUMULATED_IMAGING_TASKS
    global ACCUMULATED_MAINTENANCE_TASKS
    global MAINTENANCE_TASK_HISTORY
    global IMAGING_TASK_HISTORY
    global SATELLITES
    global GLOBAL_TIME

    for s in SATELLITES:
        tasks_to_remove = []
        schedule = json.loads(s.schedule)
        for t in schedule:
            if isinstance(t[0], ImageTask):
                process_image_task(tasks_to_remove, t)
            elif isinstance(t[0], MaintenanceTask): # if the maintenance task has not been executed (hasn's started) yet
                process_maintenance_task(tasks_to_remove, t)

        for task in tasks_to_remove:
            schedule.remove(task)
            s.capacity_used -= get_image_type(task.image_type)['size']
        s.schedule = json.dumps(schedule)

        tasks_to_remove = []
        no_outage_tasks = json.loads(s.maintenance_without_outage)
        for t in no_outage_tasks:
            process_maintenance_task(tasks_to_remove, t)
        for task in tasks_to_remove:
            no_outage_tasks.remove(task)
            s.capacity_used -= get_image_type(task.image_type)['size']
        s.maintenance_without_outage = json.dumps(no_outage_tasks)

    # sort task list by priority
    ACCUMULATED_IMAGING_TASKS = dict(sorted(ACCUMULATED_IMAGING_TASKS.items(), key=lambda item: item[0], reverse=True))
    ACCUMULATED_MAINTENANCE_TASKS = dict(sorted(ACCUMULATED_MAINTENANCE_TASKS.items(), key=lambda item: item[0], reverse=True))

def process_image_task(tasks_to_remove, t):
    global ACCUMULATED_IMAGING_TASKS
    global IMAGING_TASK_HISTORY
    global GLOBAL_TIME

    if t[1] > GLOBAL_TIME: # if the imaging task has not been executed (hasn's started) yet
        add_task_to_priority_list(ACCUMULATED_IMAGING_TASKS,t[0])
        tasks_to_remove.append(t)
        t[0].satellite = None
    elif t[2] < GLOBAL_TIME:
        tasks_to_remove.append(t)
        IMAGING_TASK_HISTORY.append(t)


def process_maintenance_task(tasks_to_remove, t):
    global GLOBAL_TIME
    global ACCUMULATED_MAINTENANCE_TASKS
    global MAINTENANCE_TASK_HISTORY

    if t[1] > GLOBAL_TIME: # if the task has not been executed yet
        tasks_to_remove.append(t)
        if t[0].is_head:
            add_task_to_priority_list(ACCUMULATED_MAINTENANCE_TASKS,t[0]) # add it to the reschedule list
    elif t[1] <= GLOBAL_TIME and t[2] > GLOBAL_TIME: # if the task is being executed
        if t[0].is_head:
            t[0].is_head = False
            get_task_by_name(t[0].next_maintenance).is_head = True # assign its next occurence to be the head
    elif t[2] <= GLOBAL_TIME: # if the task is completed
        tasks_to_remove.append(t)
        MAINTENANCE_TASK_HISTORY.append(t)
        if t[0].is_head:
            t[0].is_head = False
            get_task_by_name(t[0].next_maintenance).is_head = True # assign its next occurence to be the head



def clear_expired_tasks(task_list):
    global GLOBAL_TIME
    global IMAGING_TASK_HISTORY
    global MAINTENANCE_TASK_HISTORY
    for p_group in task_list.items(): 
        tasks = p_group[1]
        expired_tasks = []
        for task in tasks:
            if task.end_time - task.duration < GLOBAL_TIME: # if we have passed the lastest possible start time of the task
                expired_tasks.append(task)
                if isinstance(task, ImageTask):
                    IMAGING_TASK_HISTORY.append(task)
                elif isinstance(task, MaintenanceTask):
                    MAINTENANCE_TASK_HISTORY.append(task)
        for expired_task in expired_tasks:
            tasks.remove(expired_task)


def add_task_to_priority_list(priority_list, task):
    if priority_list.get(task.priority) is None:
        priority_list[task.priority] = [task]
    else:
        priority_list[task.priority].append(task)



def convert_json_to_imaging_task(task_json, name, satellites):
    global ACCUMULATED_IMAGING_TASKS
    task_list = []

    # TODO: CREATE A UNIQUE ID FOR EACH TASK  
    # name = "ImagingTask" + str(random.randint(0, 10000)) 
      
    data = json.load(task_json)
    priority = data["Priority"]
    start_time = convert_str_to_datetime(data["ImageStartTime"])
    end_time = convert_str_to_datetime(data["ImageEndTime"])
    image_type = data["ImageType"]
    # print(f'THE IMAGE TYPE IS: {image_type}')
    duration = dt.timedelta(seconds=int(get_image_type(image_type)['time_for_writing']))
    lat = data["Latitude"]
    lon = data["Longitude"]
    # revisit frequency
    recurrence = data["Recurrence"]["Revisit"] 
    if recurrence == "False":
        new_imaging_task = define_and_add_imagaing_task(satellites, image_type, lat, lon, name, start_time, end_time, duration, priority)
        task_list.append(new_imaging_task)
    elif recurrence == "True":
        num_revisit = int(data["Recurrence"]["NumberOfRevisits"])
        revisit_frequency = data["Recurrence"]["RevisitFrequency"]
        frequency_unit = data["Recurrence"]["RevisitFrequencyUnits"]
        new_imaging_task = define_and_add_imagaing_task(satellites, image_type, lat, lon, name, start_time, end_time, duration, priority)
        task_list.append(new_imaging_task)
        tasks = construct_and_add_revisit_imaging_tasks(num_revisit, revisit_frequency, frequency_unit, satellites, image_type, lat, lon, name, start_time, end_time, duration, priority)
        task_list += tasks
    return task_list

def add_new_maintenance_task(satellites, task_group):
    global IMAGING_TASK_HISTORY
    global MAINTENANCE_TASK_HISTORY
    global ACCUMULATED_IMAGING_TASKS
    global ACCUMULATED_MAINTENANCE_TASKS
    # global SATELLITES
    global GLOBAL_TIME
    
    # clear expired tasks from the task lists
    clear_expired_tasks(ACCUMULATED_IMAGING_TASKS)
    clear_expired_tasks(ACCUMULATED_MAINTENANCE_TASKS)
    
    # determine if the task has passed the current time, if yes, return false
    for task in task_group:
        # while task:
        if not task.end_time or task.end_time - task.duration > GLOBAL_TIME: # if the task hasn't been assigned an end time yet OR the lastest start time is later than current time
            # then this task is potentially feasible, add it to the list
            add_task_to_priority_list(ACCUMULATED_MAINTENANCE_TASKS,task)
            # break # only add the first executable task into the list (the repetition will be added once this task has been scheduled)
        # task = get_task_by_name(task.next_maintenance)
        ACCUMULATED_MAINTENANCE_TASKS = dict(sorted(ACCUMULATED_MAINTENANCE_TASKS.items(), key=lambda item: item[0], reverse=True))
    
    # clear tasks that has been finished and that is being executed at current time
    update_maintenenace_and_imaging_pool()
           
    # do EDF
    ACCUMULATED_MAINTENANCE_TASKS = edf_maintenance(ACCUMULATED_MAINTENANCE_TASKS, satellites)
    # remove non-outage maintenance activities from the schedule and add them to another list
    for s in satellites:
        schedule = json.loads(s.schedule)
        no_outage_tasks = json.loads(s.maintenance_without_outage)
        for t in schedule:
            if isinstance(t[0], MaintenanceTask) and not t[0].payload_outage:
                no_outage_tasks.append(t)
        for t in no_outage_tasks:
            schedule.remove(t)
        s.schedule = json.dumps(schedule)
        s.maintenance_without_outage = json.dumps(no_outage_tasks)

    ACCUMULATED_IMAGING_TASKS = edf_imaging(ACCUMULATED_IMAGING_TASKS, satellites)
    return 0

def convert_json_to_maintenance_task(task_json, name, satellites):
    data = json.load(task_json)
    # for simplicity, we only consider the window (start and end time) and duration 
    target = get_satellite_by_name(satellites, data["Target"])
    start_time = convert_str_to_datetime(data["Window"]["Start"])
    end_time = convert_str_to_datetime(data["Window"]["End"])
    duration = dt.timedelta(seconds=int(data["Duration"]))
    payload_outage = False if data["PayloadOutage"]=="FALSE" else True
    # revisit frequency
    num_repetition = data["RepeatCycle"]["Repetition"] 

    if num_repetition == "Null":
        new_task = MaintenanceTask(name=name, 
                                   start_time=start_time, 
                                   end_time=end_time, 
                                   duration=duration, 
                                   priority=4, 
                                   min_gap=0, 
                                   max_gap=0, 
                                   next_maintenance='', 
                                   is_head=True, 
                                   satellite=target, 
                                   payload_outage=payload_outage
                                   )
        return [new_task]
    else:
        min_gap = data["RepeatCycle"]["Frequency"]["MinimumGap"]
        max_gap = data["RepeatCycle"]["Frequency"]["MaximumGap"]

        new_tasks = construct_and_add_revisit_maintenance_tasks(num_repetition=num_repetition, 
                                                               payload_outage=payload_outage, 
                                                               min_gap=min_gap, 
                                                               max_gap=max_gap, 
                                                               name=name, 
                                                               start_time=start_time, 
                                                               end_time=end_time, 
                                                               duration=duration, 
                                                               target=target)
        return new_tasks

def set_satellites(satellites):
    global SATELLITES
    # for s in satellites:
    #     s.schedule = json.loads(s.schedule)
    SATELLITES = satellites


def initialize_satellites(satellite_path):
    satellites = []
    for tle_path in glob.glob(os.path.join(satellite_path, '*.txt')):
        with open(tle_path, 'r') as file:
            tle = file.read().split('\n')
            satellite_name = tle_path.split('/')[-1].split('.')[0].split('_')[0]
            satellites.append(Satellite(name=satellite_name, tle=tle, storage_capacity=STORAGE_CAPACITY))
    return satellites


def initialize_imaging_tasks(imaging_path, satellites):
    imaging_json_files = read_directory(imaging_path)
    print(f'{imaging_path} contains {len(imaging_json_files)} files.')
    # POINT = 0
    imaging_tasks = []
    for json_file in imaging_json_files:
        # POINT += 1
        # if POINT == 20: set_global_time("2023-10-02 10:00:00")
        file_path = os.path.join(imaging_path, json_file)
        # print(json_file.split('/')[-1].split('.')[0])
        with open(file_path, 'r') as file:
            task_name = json_file.split('/')[-1].split('.')[0]
            # print(f"\nscheduling task {task_name}...")
            # add_new_imaging_task(file, name = task_name)
            # convert the json file to an imaging task object
            tasks = convert_json_to_imaging_task(file, task_name, satellites)
            imaging_tasks.extend(tasks)

            # for satellite in SATELLITES:
            #     print(f"------{satellite.name} capacity: {satellite.capacity_used}/{satellite.capacity}------")
            #     for t in satellite.schedule:
            #         print(f"{t[0].name}         {t[1]} --> {t[2]}")

    return imaging_tasks

def initialize_maintenance_tasks(maintenance_path, satellites):
    maintenance_json_files = read_directory(maintenance_path)
    print(f'{maintenance_path} contains {len(maintenance_json_files)} files.')
    maintenance_tasks = []
    for json_file in maintenance_json_files:
        # POINT += 1
        # if POINT == 20: set_global_time("2023-10-02 10:00:00")
        file_path = os.path.join(maintenance_path, json_file)
        with open(file_path, 'r') as file:
            task_name = json_file.split('/')[-1].split('.')[0]
            tasks = convert_json_to_maintenance_task(file, task_name, satellites)
            maintenance_tasks.extend(tasks)
    return maintenance_tasks

def get_task_by_name_from_specific_list(name, task_list):
    for t in task_list:
        if t.name == name:
            return t
    return None

def associate_maintenance_tasks(maintenance_tasks):
    task_groups = []
    for t in maintenance_tasks:
        if t.is_head:
            this_task_group = []
            this_task_group.append(t)
            next_name = t.next_maintenance
            while len(next_name)>0:
                next_task = get_task_by_name_from_specific_list(next_name, maintenance_tasks)
                this_task_group.append(next_task)
                next_name = next_task.next_maintenance
            task_groups.append(this_task_group)
    return task_groups
            

                

''' datetime and str conversion'''

def convert_datetime_to_str(datetime_object):
    # return str(datetime)
    return datetime_object.strftime("%Y-%m-%dT%H:%M:%S")

def convert_str_to_datetime(str):
    naive = datetime.strptime(str, "%Y-%m-%dT%H:%M:%S")
    return naive.replace(tzinfo=timezone.utc)
     


# def initialize_maintenance_tasks(maintenance_path):
#     global ACCUMULATED_MAINTENANCE_TASKS
#     return















# # TESTS
# ############################### Initialize satellites group 1 ################################
# # for TLE 1
# # with open('/app/TLE/tle1/SOSO-1_TLE.txt', 'r') as file: tle1 = file.read().split('\n')
# # with open('/app/TLE/tle1/SOSO-2_TLE.txt', 'r') as file: tle2 = file.read().split('\n')
# # with open('/app/TLE/tle1/SOSO-3_TLE.txt', 'r') as file: tle3 = file.read().split('\n')
# # with open('/app/TLE/tle1/SOSO-4_TLE.txt', 'r') as file: tle4 = file.read().split('\n')
# # with open('/app/TLE/tle1/SOSO-5_TLE.txt', 'r') as file: tle5 = file.read().split('\n')

# # for TLE 2
# # with open('/app/TLE/tle2/SOSO-6_TLE.txt', 'r') as file: tle1 = file.read().split('\n')
# # with open('/app/TLE/tle2/SOSO-7_TLE.txt', 'r') as file: tle2 = file.read().split('\n')
# # with open('/app/TLE/tle2/SOSO-8_TLE.txt', 'r') as file: tle3 = file.read().split('\n')
# # with open('/app/TLE/tle2/SOSO-9_TLE.txt', 'r') as file: tle4 = file.read().split('\n')
# # with open('/app/TLE/tle2/SOSO-10_TLE.txt', 'r') as file: tle5 = file.read().split('\n')

# # for TLE 3
# with open('/app/TLE/tle3/SOSO-1_TLE.txt', 'r') as file: tle1 = file.read().split('\n')
# with open('/app/TLE/tle3/SOSO-2_TLE.txt', 'r') as file: tle2 = file.read().split('\n')
# with open('/app/TLE/tle3/SOSO-3_TLE.txt', 'r') as file: tle3 = file.read().split('\n')
# with open('/app/TLE/tle3/SOSO-4_TLE.txt', 'r') as file: tle4 = file.read().split('\n')
# with open('/app/TLE/tle3/SOSO-5_TLE.txt', 'r') as file: tle5 = file.read().split('\n')

# time_window_start = datetime(2023, 11, 18, 00, 00, 00, tzinfo=timezone.utc)
# time_window_end = datetime(2023, 11, 19, 23, 59, 59, tzinfo=timezone.utc) 

# satellites1 = [Satellite('SOSO-1', tle1),
#             Satellite('SOSO-2', tle2),
#             Satellite('SOSO-3', tle3),
#             Satellite('SOSO-4', tle4),
#             Satellite('SOSO-5', tle5)]

# ############################### Initialize satellites group 2 ################################
# # for group 2 images
# # time_window_start = datetime(2023, 11, 18, 00, 00, 00)
# # time_window_end = datetime(2023, 11, 18, 23, 59, 59) 

# # for group 3 old images
# # time_window_start = datetime(2023, 10, 8, 00, 00, 00)
# # time_window_end = datetime(2023, 10, 9, 23, 59, 59) 

# # for group 4 new images
# time_window_start = datetime(2023, 10, 2, 00, 00, 00, tzinfo=timezone.utc)
# time_window_end = datetime(2023, 10, 2, 23, 59, 59, tzinfo=timezone.utc) 

# satellites2 = [Satellite('SOSO-1',tle1),
#             Satellite('SOSO-2',tle2),
#             Satellite('SOSO-3',tle3),
#             Satellite('SOSO-4',tle4),
#             Satellite('SOSO-5',tle5)]
    
# SATELLITES = satellites2
# set_global_time("2023-10-02 00:00:00")

# ############################## process maintenance acticvities ############################### 
# # maintenance_path = "/app/order_samples/m_group2" # group 1 is a set of maintenance activities
# # maintenance_json_files = read_directory(maintenance_path)
# # print(f'{maintenance_path} contains {len(maintenance_json_files)} files.')

# # POINT = 0
# # for json_file in maintenance_json_files[:17]:
# #     POINT += 1
# #     if POINT == 15: set_global_time("2023-11-18 00:10:00")
# #     file_path = os.path.join(maintenance_path, json_file)
# #     with open(file_path, 'r') as file:
# #         task_name = json_file.split('/')[-1].split('.')[0]
# #         print(f"\nscheduling task {task_name}...")
# #         add_new_maintenance_task(file, task_name)

# #         for satellite in SATELLITES:
# #             print(f"------{satellite.name} capacity: {satellite.capacity_used}/{satellite.capacity}------")
# #             for t in satellite.schedule:
# #                 print(f"{t[0].name}         {t[1]} --> {t[2]}")
        

# ############################### process imaging tasks ###############################
# imaging_path = "/app/order_samples/group4_newest" # group 2 is a set of imaging tasks
# imaging_json_files = read_directory(imaging_path)
# print(f'{imaging_path} contains {len(imaging_json_files)} files.')

# POINT = 0
# for json_file in imaging_json_files[:50]:
#     POINT += 1
#     if POINT == 20: set_global_time("2023-10-02 10:00:00")
#     file_path = os.path.join(imaging_path, json_file)
#     # print(json_file.split('/')[-1].split('.')[0])
#     with open(file_path, 'r') as file:
#         task_name = json_file.split('/')[-1].split('.')[0]
#         print(f"\nscheduling task {task_name}...")
#         add_new_imaging_task(file, name = task_name)

#         for satellite in SATELLITES:
#             print(f"------{satellite.name} capacity: {satellite.capacity_used}/{satellite.capacity}------")
#             for t in satellite.schedule:
#                 print(f"{t[0].name}         {t[1]} --> {t[2]}")



# print("=================== LEFT OVER TASKS =======================")
# for key in ACCUMULATED_IMAGING_TASKS:
#     print(f"==========={key}===========")
#     for task in ACCUMULATED_IMAGING_TASKS[key]:
#         print(task.name)

# print("=================== FINAL SCHEDULES =======================")
# total=0
# for satellite in SATELLITES:
#     print(f"------{satellite.name} capacity: {satellite.capacity_used}/{satellite.capacity}------")
#     total += len(satellite.schedule)
#     for t in satellite.schedule:
#         print(f"{t[0].name}         {t[1]} --> {t[2]}")
#         # print(t[0].name, t[1], t[2])
#     print("(Maintenances without payload outage: )")
#     total += len(satellite.maintenance_without_outage)
#     for t in satellite.maintenance_without_outage:
#         print(f"{t[0].name}         {t[1]} --> {t[2]}")
# print(f'{total} tasks got scheduled.')


# print("=================== COMPLETED TASKS =======================")
# print("Images:")
# for t in IMAGING_TASK_HISTORY:
#     print(f"{t[0].name}         {t[1]} --> {t[2]}")
# print("Maintenances:")
# for t in MAINTENANCE_TASK_HISTORY:
#     print(f"{t[0].name}         {t[1]} --> {t[2]}")
