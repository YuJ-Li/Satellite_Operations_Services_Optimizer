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



# Define the fitness function
def fitness(schedule):
    total = 0
    for task in schedule:
        if task is not None:
            if task.priority == 4:
                total += 50**3
            elif task.priority == 3:
                total += 50**2
            elif task.priority == 2:
                total += 50
            else:
                total += 1
    return total

# Define the mutation function
def mutate(schedule):
    for i in range(len(schedule)):
        if schedule[i] is not None:
            task = schedule[i]
            if (task.end_time - task.start_time) == task.duration:
                new_start_time = task.start_time
            else:

                # Change the start time of the task within the allowed window
                new_start_time = random_date(task.start_time, task.end_time - task.duration)
            # Ensure the new start time allows for the full duration of the task
            schedule[i].start_time = new_start_time


# Define the crossover function
def crossover(schedule1, schedule2):
    if len(schedule1) > 2:
        index = random.randint(1, len(schedule1) - 2)
        new_schedule1 = schedule1[:index] + schedule2[index:]
        new_schedule2 = schedule2[:index] + schedule1[index:]

        # Resolve conflicts in the offspring schedules
        resolve_conflicts(new_schedule1)
        resolve_conflicts(new_schedule2)
        return new_schedule1, new_schedule2
    else:
        return schedule1, schedule2

def resolve_conflicts(schedule):
    """
    Resolve conflicts in the schedule by adjusting start times.
    """
    sorted_schedule = sorted(schedule, key=lambda task: task.start_time)
    for i in range(1, len(sorted_schedule)):
        if sorted_schedule[i].start_time < sorted_schedule[i - 1].end_time:
            # There is a conflict, adjust the start time
            new_start = sorted_schedule[i - 1].end_time
            start_end = sorted_schedule[i].end_time - sorted_schedule[i].duration
            if start_end > new_start:
                valid_start_range = random_date(new_start,start_end)
                sorted_schedule[i].start_time = valid_start_range

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
# 1 duration
# 2 time slot
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
                satellite_schedule_temp[assigned_satellite].append((task.name, s_time, s_time + task.duration))
                newly_assigned_tasks.append(task)

        # Remove newly assigned tasks from tasks
        tasks = [task for task in tasks if task not in newly_assigned_tasks]
        population.append(satellite_schedule_temp)
        
    return population


def print_population(p):
    for i, dictionary in enumerate(p):
        print("Population" + str(i))
        for satellite in dictionary:
            print(satellite)
            temp = []
            for task in dictionary[satellite]:
                temp.append(task)
            print(temp)

def genetic_algorithm(population, fitness_function, mutate_function, crossover_function, generations):
    for generation in range(generations):  # Generations
        if random.random() < 0.5:
            # Mutation
            if population:
                schedule = random.choice(population)[:]
                mutate_function(schedule)
                population.append(schedule)
            else:
                # If the population is empty, generate a new random schedule
                new_schedule = [task for satellite in satellites for task in satellite.schedule]
                population.append(new_schedule)
        else:
            # Crossover
            if len(population) >= 2:
                schedule1, schedule2 = random.sample(population, 2)
                offspring1, offspring2 = crossover_function(schedule1, schedule2)
                population.append(offspring1)
                population.append(offspring2)

        # Select the top 100 schedules based on fitness for the next generation
        population = sorted(population, key=fitness_function, reverse=True)[:100]

    return population

def print_schedule_info(unassigned_tasks, satellite_schedules):
    print("Unassigned Tasks:")
    for task in unassigned_tasks:
        print(f"Task {task.name}")

    # Print satellite schedules
    for satellite, schedule in satellite_schedules.items():
        print(f"\nSatellite {satellite} Schedule:")
        for task in schedule:
            print(f"Task {task.name} from {task.start_time} to {task.end_time}")

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



    ############################### Initialize satellites ################################

    population_size = 500
    generations = 1000

    population = initialize_population(satellites, maintenance_activities, population_size)
    
    print(len(population))
    print_population(population)

    # genetic_algorithm(population, fitness, mutate, crossover, generations)

    # # Identify unassigned tasks
    # unassigned_tasks = [task for task in maintenance_activities if task not in [t for sat in satellites for t in sat.schedule]]

    # # Print schedule information
    # print_schedule_info(unassigned_tasks, {satellite.name: satellite.schedule for satellite in satellites})
