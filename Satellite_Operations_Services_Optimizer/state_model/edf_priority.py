# from .repositories import *
import json
import os
from datetime import datetime, timezone
import datetime as dt
from scheduling_algorithm import *



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
                            satellite.schedule.insert(schedule_ptr, (task, scheduled_start, scheduled_end)) 
                            scheduled = True
                            # print(f'{task.name} is scheduled on {satellite.name}.')
                            break
                        elif task.start_time >= empty_slot_start and task.start_time + task.duration <= empty_slot_end and task.start_time + task.duration <= task.end_time:
                            scheduled_start = task.start_time
                            scheduled_end = scheduled_start + task.duration
                            satellite.schedule.insert(schedule_ptr, (task, scheduled_start, scheduled_end)) 
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


satellites1, satellites2, maintenance_activities, imaging_tasks = initialize_satellites_tasks()
print('----------------- SCHEDULING START -----------------')

# TODO 1: use your scheduling algorithm to schedule tasks in `maintenance_activities` on the five satellites
print('---------maintenance activities----------')
priority_list1 = group_by_priority(maintenance_activities)

# print_priority_list(priority_list)

edf(priority_list1, satellites1)

print('------------------')
total=0
for satellite in satellites1:
    print(satellite.name, ':')
    total += len(satellite.schedule)
    for t in satellite.schedule:
        print(t[0].name)
print(f'{total} maintenance tasks got scheduled.')

# TODO 2: use your scheduling algorithm to schedule tasks in `imaging_tasks` on the five satellites
print('-----------imaging tasks-------------')
priority_list2 = group_by_priority(imaging_tasks)

# print_priority_list(priority_list)

edf(priority_list2, satellites2)

print('------------------')
total=0
for satellite in satellites2:
    print(satellite.name, ':')
    total += len(satellite.schedule)
    for t in satellite.schedule:
        print(t[0].name)
print(f'{total} imaging tasks got scheduled.')

# TODO 3: use your scheduling algorithm to schedule tasks in BOTH lists on the five satellites
# all_tasks = imaging_tasks
# all_tasks.extend(maintenance_activities)
# priority_list = group_by_priority(all_tasks)

# edf(priority_list, satellites)

# print('------------------')
# total=0
# for satellite in satellites:
#     print(satellite.name, ':')
#     total += len(satellite.schedule)
#     for t in satellite.schedule:
#         print(t[0])
# print(f'{total} tasks got scheduled.')
 

num_achievable_task = 0
for it in imaging_tasks:
    achievable = False
    print("Task name: ", it.name)
    for s in satellites:
        common_achievabilities = find_satellite_achievabilities(s, it)
        if len(common_achievabilities)!=0:
            achievable = True
            print(f"{s.name}: {(common_achievabilities)}")
    if achievable: num_achievable_task+=1
print(num_achievable_task)

# check satellite availibility (fov)
# take care of revisit frequency sample 24
# take care of capacity of satellites
