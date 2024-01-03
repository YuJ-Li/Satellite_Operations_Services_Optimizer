import random
from datetime import datetime
import datetime as dt
import json
import os
import copy
from enum import Enum

class Task:
    def __init__(self, name, start_time, end_time, duration, priority, satellite = None):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.priority = priority # imaging tasks: priority from 3 to 1 = from high to low; maintenance activity: priority = 4 (highest)
        self.satellite = satellite # to be determined by the scheduling algorithm

class ImageTask(Task):
    def __init__(self, image_type, name, start_time, end_time, duration, priority, satellite = None):
        super().__init__(name = name, start_time = start_time, end_time = end_time, duration = duration, priority = priority, satellite = satellite)
        self.image_type = image_type

class ImageType(Enum):
    SPOTLIGHT = {'time_for_writing':120, 'size':512, 'dimension':[10,10]}
    MEDIUM = {'time_for_writing':45, 'size':256, 'dimension':[40,20]}
    LOW = {'time_for_writing':20, 'size':128, 'dimension':[40,20]}

class Satellite:
    def __init__(self, name, activity_window):
        self.name = name
        self.activity_window = activity_window
        self.schedule = [] # list of ((#task_name, actual_start_time, real_end_time))


def read_directory(path):
    json_files = [f.path for f in os.scandir(path) if f.is_file() and f.name.endswith(('.json', '.JSON'))]
    return json_files

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

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + dt.timedelta(seconds=random_second)

########################################################################################
def detect_no_conflicts(schedule, task, satellite):
    act_window = satellite.activity_window
    if not schedule:
        if task.start_time >= act_window[0] and task.start_time + task.duration <= act_window[1]:
            return task.start_time
        elif task.start_time < act_window[0] and act_window[0] + task.duration <= act_window[1] and act_window[0] + task.duration <= task.end_time:
            return act_window[0]
        else:
            return None
    else:
        schedule.sort(key=lambda x: (x[2],x[1]))

        for i, _ in enumerate(schedule):

            if i==0 and task.start_time >= act_window[0] and task.start_time + task.duration <= schedule[i][1]:
                return task.start_time
            elif i==0 and task.start_time < act_window[0] and act_window[0] + task.duration <= schedule[i][1] and act_window[0] + task.duration <= task.end_time:
                return act_window[0]    
            elif (i-1 >= 0 and i < len(schedule)-1 and task.start_time <= schedule[i-1][2] and schedule[i-1][2] + task.duration <= schedule[i][1] and schedule[i-1][2] + task.duration <= task.end_time):
                return schedule[i-1][2]
            elif (i == len(schedule)-1 and schedule[i][2] + task.duration <= act_window[1] and schedule[i][2] + task.duration <= task.end_time and schedule[i][2] >= task.start_time):
                return schedule[i][2]
        return None


def initialize_population(satellites, tasks, population_size):
    s_time = None
    temp_tasks = copy.deepcopy(tasks)
    population = []
    for _ in range(population_size):
        tasks = temp_tasks
        random.shuffle(tasks)
        newly_assigned_tasks = []
        satellite_schedule_temp = {}

        for satellite in satellites:
            satellite_schedule_temp[satellite.name] = copy.deepcopy(satellite.schedule)
        
        for task in tasks:
            assigned_satellite = copy.deepcopy(task.satellite.name) if (task.satellite) else None
            for satellite in satellite_schedule_temp:
                if (assigned_satellite is not None and satellite != assigned_satellite):
                    continue
                # Check if the task's time conflicts with the times of tasks already in the schedule
                s_time = detect_no_conflicts(satellite_schedule_temp[satellite], task, get_satellite_by_name(satellites, satellite))
                if (s_time):
                    assigned_satellite = satellite
                else:
                    assigned_satellite = None

            if assigned_satellite is not None and s_time is not None:
                satellite_schedule_temp[assigned_satellite].append((task, s_time, s_time + task.duration))
                newly_assigned_tasks.append(task)

        # Remove newly assigned tasks from tasks
        tasks = [task for task in tasks if task not in newly_assigned_tasks]
        population.append(satellite_schedule_temp)
        
    return population


# Define the fitness function
def fitness(schedule):
    total = 0
    for satellite in schedule:
        for task in schedule[satellite]:
            if task[0].priority == 4:
                total += 50**3
            elif task[0].priority == 3:
                total += 50**2
            elif task[0].priority == 2:
                total += 50
            else:
                total += 1
    return total

# Define the mutation function
def mutate(schedule, tasks, satellites):
    random_key = random.choice(list(schedule.keys()))
    temp_tasks = tasks
    scheduled_tasks=[]
    for satellite in schedule:
        for task in schedule[satellite]:
            if satellite == random_key:
                continue
            else:
                scheduled_tasks.append(task[0])
    tasks_to_reschedule=[task for task in temp_tasks if task not in scheduled_tasks]
    random.shuffle(tasks_to_reschedule)
    new_schedule = []
    for task in tasks_to_reschedule:
        assigned_satellite = copy.deepcopy(task.satellite.name) if (task.satellite) else None
        if assigned_satellite is not None and assigned_satellite != random_key:
            continue
        else:
            s_time = detect_no_conflicts(new_schedule, task, get_satellite_by_name(satellites, random_key))
            if (s_time):
                assigned_satellite = random_key
            else:
                assigned_satellite = None
        if assigned_satellite is not None and s_time is not None:
            new_schedule.append((task, s_time, s_time + task.duration))      
    schedule[random_key] = new_schedule
    return schedule

'''
cross over satellites

mutate one of the satellite schedule:
randomly put it non repeated remaining tasks to see if a better outcome can be acheived
'''
# Define the crossover function
def crossover(schedule1, schedule2):
    crossover_point = len(schedule1)//2

    keys_to_exchange = list(schedule1.keys())[:crossover_point]
    for key in keys_to_exchange:
        schedule1[key], schedule2[key] = schedule2[key], schedule1[key]
    return resolve_conflicts(schedule1), resolve_conflicts(schedule2)

def resolve_conflicts(schedule):
    # key_list = list(schedule.keys())
    # random.shuffle(key_list)
    existing_tasks=[]
    for satellite in schedule:
        tasks_to_remove = []
        for task in schedule[satellite]:
            if task[0].name not in existing_tasks:
                existing_tasks.append(task[0].name)
            else:
                tasks_to_remove.append(task)
        for task in tasks_to_remove:
            schedule[satellite].remove(task)
    return schedule

def print_population(p):
    for i, dictionary in enumerate(p):
        print("Population" + str(i))
        for satellite in dictionary:
            print(satellite)
            temp = []
            for task in dictionary[satellite]:
                temp.append((task[0].name, task[1], task[2]))
            print(temp)

def print_schedule(s):
    for satellite in s:
        print(satellite)
        temp = []
        for task in s[satellite]:
            temp.append((task[0].name, task[1], task[2]))
        temp.sort(key=lambda x: (x[1], x[2]))
        print(temp)
        print(len(temp))


def genetic_algorithm(population, fitness_function, mutate_function, crossover_function, generations, tasks, satellites):
    for generation in range(generations):  # Generations
        for schedule in population:
            if random.random() <= 1:
                # Mutation
                mutate_function(schedule, tasks, satellites)
                population.remove(schedule)
                population.append(schedule)
        # Crossover
        schedule1, schedule2 = random.sample(population, 2)
        offspring1, offspring2 = crossover_function(schedule1, schedule2)
        population.append(offspring1)
        population.append(offspring2)

        # Select the top 100 schedules based on fitness for the next generation
        population = sorted(population, key=fitness_function, reverse=True)[:len(population)]

    return population[0]

if __name__ == "__main__":
    time_window_start = datetime(2023, 10, 8, 00, 00, 00)
    time_window_end = datetime(2023, 10, 9, 23, 59, 59) 
    satellites = [Satellite('SOSO-1',(time_window_start,time_window_end)),
                Satellite('SOSO-2',(time_window_start,time_window_end)),
                Satellite('SOSO-3',(time_window_start,time_window_end)),
                Satellite('SOSO-4',(time_window_start,time_window_end)),
                Satellite('SOSO-5',(time_window_start,time_window_end))]


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
            print(file_path, name)
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

    all_tasks = imaging_tasks
    all_tasks.extend(maintenance_activities)

    ############################### Initialize satellites ################################

    population_size = 200
    generations = 1000

    population = initialize_population(satellites, all_tasks, population_size)
    schedule = genetic_algorithm(population, fitness, mutate, crossover, generations, all_tasks, satellites)
    print_schedule(schedule)

    # # Identify unassigned tasks
    # unassigned_tasks = [task for task in maintenance_activities if task not in [t for sat in satellites for t in sat.schedule]]

    # # Print schedule information
    # print_schedule_info(unassigned_tasks, {satellite.name: satellite.schedule for satellite in satellites})



    # dict1 = {'a':1, 'b':2, 'c':3, 'd':4}
    # dict2 = {'a':5, 'b':6, 'c':7, 'd':8}
    # x,y=crossover(dict1, dict2)
    # print(x,y)