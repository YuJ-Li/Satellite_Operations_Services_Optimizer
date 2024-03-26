import random
from datetime import datetime
import datetime as dt
import json
import os
import copy
from enum import Enum
from scheduling_algorithm import *

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
    real_tasks=[]
    for t in temp_tasks:
        if hasattr(t, 'achievability'):
            valid_keys = [key for key, value in t.achievability.items() if value != []]
            if valid_keys:
                random_sat = random.choice(valid_keys)
                random_t = random.choice(t.achievability[random_sat])
                t.start_time = random_t[0]
                t.end_time = random_t[1]
                real_tasks.append(t)
            else:
                continue
        else:
            real_tasks.append(t)
    population = []
    for _ in range(population_size):
        tasks = real_tasks
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
        
    return population, real_tasks


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

    satellites1, satellites2, maintenance_activities, imaging_tasks = initialize_satellites_tasks()
    ############################### Initialize satellites ################################

    population_size = 200
    generations = 1000

    ############# For maintenance_activities#############
    population, real_tasks = initialize_population(satellites1, maintenance_activities, population_size)
    schedule = genetic_algorithm(population, fitness, mutate, crossover, generations, real_tasks, satellites1)
    print_schedule(schedule)

    ############# For imaging_tasks######################
    population, real_tasks = initialize_population(satellites2, imaging_tasks, population_size)
    schedule = genetic_algorithm(population, fitness, mutate, crossover, generations, real_tasks, satellites2)
    print_schedule(schedule)
