class Task:
    def __init__(self, name, start_time, end_time, duration, priority, satellite = None):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.priority = priority # priority from 3 to 1 = from high to low
        self.satellite = satellite

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
    # sorts tasks in each priority group by deadline
    for p_group in priority_list.items(): 
        tasks = p_group[1]
        tasks.sort(key=lambda x: (x.end_time,x.start_time)) # for each priority group, sort tasks by end time then by start time
        s = str(p_group[0]) + ": "
        for t in tasks:
            s = s + t.name + ", "
        print(s)
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
                            print(f'{task.name} is scheduled on {satellite.name}.')
                            break
                        elif task.start_time >= empty_slot_start and task.start_time + task.duration <= empty_slot_end and task.start_time + task.duration <= task.end_time:
                            scheduled_start = task.start_time
                            scheduled_end = scheduled_start + task.duration
                            satellite.schedule.insert(schedule_ptr, (task.name, scheduled_start, scheduled_end)) 
                            scheduled = True
                            # TODO: remove this task from the task list
                            print(f'{task.name} is scheduled on {satellite.name}.')
                            break
                if scheduled: break
            if not scheduled:
                print(f'Failed to schedule {task.name}.')

    
def find_next_slot(satellite, ptr):
    '''ptr is the index of task scheduled on this satellite from which we start to find empty slot'''
    satellite_schedule = satellite.schedule
    if len(satellite_schedule)==0: 
        return satellite.activity_window[0], satellite.activity_window[1], 0 # if nothing has been scheduled on the satellite yet, return the entire availility of the satellite
    if ptr == -1: # if pointer is pointing at the beginning of the schedule
        if satellite_schedule[0][1] - satellite.activity_window[0] > 0: # if there is space between the start of activity window and the start of first task
            return satellite.activity_window[0], satellite_schedule[0][1], ptr+1
        ptr += 1
    for i in range(ptr, len(satellite_schedule)-1):
        if satellite_schedule[i+1][1] - satellite_schedule[i][2] > 0: # if there is time between the start of next task and the end of this task
            return satellite_schedule[i][2],satellite_schedule[i+1][1], i+1
        ptr += 1
    if ptr == len(satellite_schedule)-1:
        if satellite.activity_window[1] - satellite_schedule[ptr][2] > 0:
            return satellite_schedule[ptr][2], satellite.activity_window[1], ptr+1
    return None, None, ptr+1
        

satellites = [Satellite('S1',(0,23)),Satellite('S2',(0,23)),Satellite('S3',(0,23)),Satellite('S4',(0,23)),Satellite('S5',(0,23))]
tasks = [
        Task("Task1", start_time=0, end_time=3, duration=3, priority=5, satellite=satellites[0]),
        Task("Task2", start_time=2, end_time=7, duration=5, priority=2),
        Task("Task3", start_time=5, end_time=7, duration=2, priority=1),
        Task("Task4", start_time=8, end_time=12, duration=4, priority=4),
        Task("Task5", start_time=1, end_time=5, duration=4, priority=4),
        Task("Task6", start_time=6, end_time=10, duration=4, priority=3),
        Task("Task7", start_time=2, end_time=6, duration=4, priority=2),
        Task("Task8", start_time=4, end_time=9, duration=5, priority=1),
        Task("Task9", start_time=9, end_time=12, duration=3, priority=4),
        Task("Task10", start_time=1, end_time=4, duration=3, priority=3),
        Task("Task11", start_time=5, end_time=9, duration=4, priority=2),
        Task("Task12", start_time=3, end_time=8, duration=5, priority=1),
        Task("Task13", start_time=7, end_time=11, duration=4, priority=4),
        Task("Task14", start_time=10, end_time=15, duration=5, priority=4),
        Task("Task15", start_time=2, end_time=5, duration=3, priority=3),
        Task("Task16", start_time=6, end_time=9, duration=3, priority=2),
        Task("Task17", start_time=4, end_time=7, duration=3, priority=1),
        Task("Task18", start_time=8, end_time=11, duration=3, priority=4),
        Task("Task19", start_time=1, end_time=5, duration=4, priority=4),
        Task("Task20", start_time=3, end_time=8, duration=5, priority=3),
]

priority_list = group_by_priority(tasks)

# print_priority_list(priority_list)

edf(priority_list, satellites)

for satellite in satellites:
    print(satellite.schedule)