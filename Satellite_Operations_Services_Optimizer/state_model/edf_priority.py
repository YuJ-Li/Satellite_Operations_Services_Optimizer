import datetime as dt
from scheduling_algorithm import *

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


def edf_imaging(priority_list, satellites):
    ''' priority_tasks is a dictionary of tasks grouped by priority'''
    unscheduled_tasks = []
    # sorts tasks in each priority group by deadline
    for p_group in priority_list.items(): 
        tasks = p_group[1]
        tasks.sort(key=lambda x: (x.end_time,x.start_time)) # for each priority group, sort tasks by end time then by start time
        for task in tasks:
            scheduled = False

            valid_keys = [key for key, value in task.achievability.items() if value != []] # list of satellites that can see this task in task's time window
            if valid_keys is None: # if this task is not in the FOV of any satellite within its available time window
                unscheduled_tasks.append(task) # consider it as non schedulable
                continue 
            # sort the satellites by increasing number of tasks scheduled on them to ensure satellites are equally used
            valid_keys = sort_satellites_by_number_of_tasks(valid_keys)
            
            for satellite in valid_keys:
                if task.satellite is not None and task.satellite != satellite: continue
                if satellite.capacity_used + task.image_type.value['size'] > satellite.capacity: continue
                schedule_ptr = -1
                while not scheduled and schedule_ptr<len(satellite.schedule):
                    empty_slot_start, empty_slot_end, schedule_ptr = find_next_slot(satellite, schedule_ptr)
                    # print(f"for {task.name} on {satellite.name}: {empty_slot_start} -- {empty_slot_end}")
                    imaging_taking_time = check_imaging_task_can_fit_in_timeslot(empty_slot_start, empty_slot_end, task, task.achievability[satellite])
                    if imaging_taking_time:
                        scheduled_start = imaging_taking_time
                        scheduled_end = scheduled_start + task.duration
                        satellite.schedule.insert(schedule_ptr, (task, scheduled_start, scheduled_end)) 
                        satellite.capacity_used += task.image_type.value['size']
                        scheduled = True
                        # print(f'{task.name} is scheduled on {satellite.name}.')
                        break
                if scheduled: break
            if not scheduled:
                unscheduled_tasks.append(task)
                # print(f'Failed to schedule {task.name}.')
            # else:
            #     # if a task got scheduled, re-sort the satellites by increasing number of tasks scheduled on them
            #     # to ensure satellites are equally used
            #     satellites = sort_satellites_by_number_of_tasks(satellites)

    print(f'{len(unscheduled_tasks)} tasks failed to be scheduled: ')
    for t in unscheduled_tasks:
        print(f"{t.name}")
    
def check_imaging_task_can_fit_in_timeslot(empty_slot_start, empty_slot_end, imaging_task, satellite_achievability):
    '''Given the start time and end time of an empty timeslot, check if the given imaging task can be fitted in the schedule of a satellite.
    @param satellite_achievability: the timeslots when the specific imaging area is in the FOV of the specific satellite
    Consider the duration of the task and the fact that taking the image (time required for the entire image to stay in the FOV) is one shot'''
    for (fov_st, fov_et) in satellite_achievability:
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

edf_maintenance(priority_list1, satellites1)

total=0
for satellite in satellites1:
    print(f"------{satellite.name}------")
    total += len(satellite.schedule)
    for t in satellite.schedule:
        print(t[0].name, t[1], t[2])
print(f'{total} maintenance tasks got scheduled.')

# TODO 2: use your scheduling algorithm to schedule tasks in `imaging_tasks` on the five satellites
print('-----------imaging tasks-------------')
priority_list2 = group_by_priority(imaging_tasks)

# print_priority_list(priority_list)

edf_imaging(priority_list2, satellites2)

total=0
for satellite in satellites2:
    print(f"------{satellite.name} capacity: {satellite.capacity_used}/{satellite.capacity}------")
    total += len(satellite.schedule)
    for t in satellite.schedule:
        print(t[0].name)
        # print(t[0].name, t[1], t[2])
print(f'{total} imaging tasks got scheduled.')



# print(f"{imaging_tasks[1].name}: \n {imaging_tasks[1].achievability}")


# check satellite availibility (fov)
# take care of revisit frequency sample 24
# take care of capacity of satellites
