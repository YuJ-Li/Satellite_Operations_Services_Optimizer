import random
import time

class Task:
    def __init__(self, name, start_time, end_time, duration, priority, satellite=None):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.priority = priority
        self.satellite = satellite

class Satellite:
    def __init__(self, name, activity_window):
        self.name = name
        self.activity_window = activity_window
        self.schedule = []

    def can_schedule(self, task):
        # Check if task fits in satellite's activity window
        if task.start_time < self.activity_window[0] or task.end_time > self.activity_window[1]:
            return False
        # Check for overlap with already scheduled tasks
        for schedule in self.schedule:
            if not (task.end_time <= schedule.start_time or task.start_time >= schedule.end_time):
                return False
        return True

    def add_task(self, task):
        self.schedule.append(task)

#helper method for task scheduler
def record_current_schedule(satellites, all_schedules,cannot_fit_tasks):
    current_schedule = [] 
    for satellite in satellites:
        satellite_schedule = [] 
        for task in satellite.schedule:
            satellite_schedule.append(task.name) 
        current_schedule.append((satellite.name, satellite_schedule,cannot_fit_tasks))
    all_schedules.append(current_schedule)

def schedule_tasks_backTrack(satellites, tasks, task_index, all_schedules,cannot_fit_tasks):
    # Base case: all tasks are scheduled
    if task_index == len(tasks):
        # Record the current schedule
        record_current_schedule(satellites,all_schedules,cannot_fit_tasks.copy())
        return
    found_satellite = False
    # Try to schedule the current task in each satellite
    for satellite in satellites:
        if satellite.can_schedule(tasks[task_index]):
            found_satellite = True
            # Add task to the satellite
            satellite.add_task(tasks[task_index])
            # Recurse to the next task
            schedule_tasks_backTrack(satellites, tasks, task_index + 1, all_schedules,cannot_fit_tasks)
            # Backtrack: Remove the last added task
            satellite.schedule.pop()

    # Handle the case where the task cannot be scheduled in any satellite
    if found_satellite ==False:
        cannot_fit_tasks.append(tasks[task_index].name)
        schedule_tasks_backTrack(satellites, tasks, task_index + 1, all_schedules,cannot_fit_tasks)
        cannot_fit_tasks.pop()
        return

#task scheduling
def schedule_tasks(satellites,tasks , num_of_fix_tasks):
    # Sort tasks by priority (higher priority first)
    
    sorted_tasks = sorted(tasks, key=lambda x: -x.priority)
    #fix the tasks
    for i in range(num_of_fix_tasks):
        task = sorted_tasks[i]
        for satellite in satellites:
            if satellite.can_schedule(task):
                satellite.add_task(task)
                break

    all_scedules = []
    cannot_fit_tasks = []
    schedule_tasks_backTrack(satellites,sorted_tasks,num_of_fix_tasks,all_scedules,cannot_fit_tasks)

    return all_scedules
    
if __name__ == "__main__":
    #satellite and task data
    satellites = [Satellite('S1', (0, 23)), Satellite('S2', (0, 23)), Satellite('S3', (0, 23)), Satellite('S4', (0, 23)), Satellite('S5', (0, 23))]
    #tasks definition
    # tasks = [
    #         Task("T1", start_time=0, end_time=3, duration=3, priority=5),
    #         Task("T2", start_time=2, end_time=7, duration=5, priority=2),
    #         Task("T3", start_time=5, end_time=7, duration=2, priority=1),
    #         Task("T4", start_time=8, end_time=12, duration=4, priority=4),
    #         Task("T5", start_time=1, end_time=5, duration=4, priority=4),
    #         Task("T6", start_time=6, end_time=10, duration=4, priority=3),
    #         Task("T7", start_time=2, end_time=6, duration=4, priority=2),
    #         Task("T8", start_time=4, end_time=9, duration=5, priority=1),
    #         Task("T9", start_time=9, end_time=12, duration=3, priority=4),
    #         Task("T10", start_time=1, end_time=4, duration=3, priority=3),
    #         Task("T11", start_time=5, end_time=9, duration=4, priority=2),
    #         Task("T12", start_time=3, end_time=8, duration=5, priority=1),
    #         Task("T13", start_time=7, end_time=11, duration=4, priority=4),
    #         Task("T14", start_time=10, end_time=15, duration=5, priority=4),
    #         Task("T15", start_time=2, end_time=5, duration=3, priority=3),
    #         Task("T16", start_time=6, end_time=9, duration=3, priority=2),
    #         Task("T17", start_time=4, end_time=7, duration=3, priority=1),
    #         Task("T18", start_time=8, end_time=11, duration=3, priority=4),
    #         Task("T19", start_time=1, end_time=5, duration=4, priority=4),
    #         Task("T20", start_time=3, end_time=8, duration=5, priority=3),
    # ]
    #generate for speed test
    task_size = 30
    tasks = []
    for i in range(1, task_size+1):
        name = f"T{i}"
        start_time = random.randint(0, 23)
        duration = random.randint(1, 8)  # Assuming max duration of 8 hours
        end_time = (start_time + duration) % 24  # Ensuring end time doesn't exceed 24 hours
        priority = random.randint(1, 5)

        task = Task(name, start_time, end_time, duration, priority)
        tasks.append(task)

    # Schedule the tasks
    fix_task_size = int(task_size/3)
    #time program
    start_time = time.time()
    all_schedules = schedule_tasks(satellites, tasks,fix_task_size)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")


    # print("returned with result: ",len(all_schedules))
    # # Display the schedulesfor
    # for i, schedule in enumerate(all_schedules):
    #     cannot_fit_tasks = 0
    #     print(f"Schedule {i}:")
    #     for sat_name, tasks, cannot_fit_tasks in schedule:
    #         cannot_fit_tasks = cannot_fit_tasks
    #         print(f"{sat_name} Schedule: {tasks}")
    #     print(f"not_fit_tasks: {cannot_fit_tasks}")
