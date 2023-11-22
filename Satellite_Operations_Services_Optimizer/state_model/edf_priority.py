# from .repositories import *
import json
import os
import secrets
from datetime import datetime
import datetime as dt

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
                            # TODO: remove this task from the task list
                            # print(f'{task.name} is scheduled on {satellite.name}.')
                            break
                        elif task.start_time >= empty_slot_start and task.start_time + task.duration <= empty_slot_end and task.start_time + task.duration <= task.end_time:
                            scheduled_start = task.start_time
                            scheduled_end = scheduled_start + task.duration
                            satellite.schedule.insert(schedule_ptr, (task.name, scheduled_start, scheduled_end)) 
                            scheduled = True
                            # TODO: remove this task from the task list
                            # print(f'{task.name} is scheduled on {satellite.name}.')
                            break
                if scheduled: break
            if not scheduled:
                unscheduled_tasks.append(task)
                # print(f'Failed to schedule {task.name}.')
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
        

def read_directory(path):
    json_files = [f.path for f in os.scandir(path) if f.is_file() and f.name.endswith(('.json', '.JSON'))]
    return json_files

def convert_str_to_datetime(datetime_str):
    date_and_time = datetime_str.split('T')
    arr = date_and_time[0].split('-')
    arr.extend(date_and_time[1].split(':'))
    datetime_obj = datetime(int(arr[0]),int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]),int(arr[5]))
    return datetime_obj

def get_imaging_writing_duration(ImageType):
    match ImageType:
        case "Low":
            return 20 # unit: seconds
        case "Medium":
            return 45 # unit: seconds
        case "Spotlight":
            return 120 # unit: seconds


''' process maintenance acticvities ''' 
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
        start_time = convert_str_to_datetime(data["Window"]["Start"])
        end_time = convert_str_to_datetime(data["Window"]["End"])
        duration = dt.timedelta(seconds=int(data["Duration"]))
        # print(f'activity name: {name}, start time: {start_time}, end time: {end_time}, duration: {duration}')
        # create a task object, with priority of 4, assuming that maintenance activities have the highest priority (higher than any imaging task)
        maintenance_activities.append(Task(name,start_time=start_time, end_time=end_time, duration=duration, priority=4))
    index += 1
print(f'There are {len(maintenance_activities)} maintenance activities.')

''' process imaging tasks '''
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
        duration = dt.timedelta(seconds=get_imaging_writing_duration(data["ImageType"]))
        # print(f'activity name: {name}, start time: {start_time}, end time: {end_time}, duration: {duration}, priority: {priority}')
        # create a task object, with priority of 4, assuming that maintenance activities have the highest priority (higher than any imaging task)
        imaging_tasks.append(Task(name,start_time=start_time, end_time=end_time, duration=duration, priority=priority))
    index += 1
print(f'There are {len(imaging_tasks)} Imaging tasks.')



############################### Initialize satellites ################################
time_window_start1 = datetime(2023, 10, 8, 6, 00, 00)
time_window_end1 = datetime(2023, 10, 8, 10, 00, 00) # S1: 2023-10-08 morning
time_window_start2 = datetime(2023, 10, 9, 18, 00, 00)
time_window_end2 = datetime(2023, 10, 9, 23, 59, 59) # S2: 2023-10-09 evening
time_window_start3 = datetime(2023, 10, 8, 20, 00, 00)
time_window_end3 = datetime(2023, 10, 8, 23, 59, 59) # S3: late 2023-10-08 
time_window_start4 = datetime(2023, 10, 8, 10, 00, 00)
time_window_end4 = datetime(2023, 10, 8, 14, 00, 00) # S4: 2023-10-08 noon
time_window_start5 = datetime(2023, 10, 9, 6, 00, 00)
time_window_end5 = datetime(2023, 10, 9, 12, 00, 00) # S5: 2023-10-09 morning
satellites = [Satellite('S1',(time_window_start1,time_window_end1)),Satellite('S2',(time_window_start2,time_window_end2)),Satellite('S3',(time_window_start3,time_window_end3)),Satellite('S4',(time_window_start4,time_window_end4)),Satellite('S5',(time_window_start5,time_window_end5))]

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
 






# tasks = [
#         Task("Task1", start_time=0, end_time=3, duration=3, priority=5, satellite=satellites[0]),
#         Task("Task2", start_time=2, end_time=7, duration=5, priority=2),
#         Task("Task3", start_time=5, end_time=7, duration=2, priority=1),
#         Task("Task4", start_time=8, end_time=12, duration=4, priority=4),
#         Task("Task5", start_time=1, end_time=5, duration=4, priority=4),
#         Task("Task6", start_time=6, end_time=10, duration=4, priority=3),
#         Task("Task7", start_time=2, end_time=6, duration=4, priority=2),
#         Task("Task8", start_time=4, end_time=9, duration=5, priority=1),
#         Task("Task9", start_time=9, end_time=12, duration=3, priority=4),
#         Task("Task10", start_time=1, end_time=4, duration=3, priority=3),
#         Task("Task11", start_time=5, end_time=9, duration=4, priority=2),
#         Task("Task12", start_time=3, end_time=8, duration=5, priority=1),
#         Task("Task13", start_time=7, end_time=11, duration=4, priority=4),
#         Task("Task14", start_time=10, end_time=15, duration=5, priority=4),
#         Task("Task15", start_time=2, end_time=5, duration=3, priority=3),
#         Task("Task16", start_time=6, end_time=9, duration=3, priority=2),
#         Task("Task17", start_time=4, end_time=7, duration=3, priority=1),
#         Task("Task18", start_time=8, end_time=11, duration=3, priority=4),
#         Task("Task19", start_time=1, end_time=5, duration=4, priority=4),
#         Task("Task20", start_time=3, end_time=8, duration=5, priority=3),
# ]