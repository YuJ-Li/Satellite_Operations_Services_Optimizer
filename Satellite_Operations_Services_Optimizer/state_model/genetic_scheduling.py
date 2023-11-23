import random
from datetime import datetime
import datetime as dt
import json
import os

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

def initialize_population(satellites, tasks, population_size):
    population = []
    for _ in range(population_size):  # population
        random.shuffle(tasks)
        newly_assigned_tasks = []

        for task in tasks:
            assigned_satellite = None

            for satellite in satellites:
                # Check if the task's time conflicts with the times of tasks already in the schedule
                if all(
                    not (task.start_time < t.end_time and t.start_time < task.end_time)
                    for t in satellite.schedule if t is not None
                ):
                    assigned_satellite = satellite.name
                    break

            if assigned_satellite is not None:
                satellite.schedule.append(task)
                newly_assigned_tasks.append(task)

        # Remove newly assigned tasks from tasks
        tasks = [task for task in tasks if task not in newly_assigned_tasks]
        
        # Check if all tasks are assigned, break if yes
        if not tasks:
            break
        
        population.append([task for satellite in satellites for task in satellite.schedule])
    return population

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
            print(f'activity name: {name}, start time: {start_time}, end time: {end_time}, duration: {duration}')
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
            data = json.load(file)
            # for simplicity, we only consider the priority, window (start and end time) and duration 
            name = "ImagingTask" + str(index)
            priority = data["Priority"]
            start_time = convert_str_to_datetime(data["ImageStartTime"])
            end_time = convert_str_to_datetime(data["ImageEndTime"])
            duration = dt.timedelta(seconds=get_imaging_writing_duration(data["ImageType"]))
            print(f'activity name: {name}, start time: {start_time}, end time: {end_time}, duration: {duration}, priority: {priority}')
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

    population_size = 500
    generations = 1000

    population = initialize_population(satellites, maintenance_activities, population_size)
    
    genetic_algorithm(population, fitness, mutate, crossover, generations)

    # Identify unassigned tasks
    unassigned_tasks = [task for task in maintenance_activities if task not in [t for sat in satellites for t in sat.schedule]]

    # Print schedule information
    print_schedule_info(unassigned_tasks, {satellite.name: satellite.schedule for satellite in satellites})
