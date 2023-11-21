import random

class Task:
    def __init__(self, name, start_time, end_time, priority, location = None):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.priority = priority
        self.location = location  # The location will be determined by the genetic algorithm

class Chromosome:
    def __init__(self, tasks):
        self.tasks = tasks
        self.fitness = self.calculate_fitness()

    def calculate_fitness(self):
        total_priority = 0
        for task in self.tasks:                
            multiplier=0
            if task.location is not None and task.priority == 4:
                multiplier = 50^3
            elif task.location is not None and task.priority == 3:
                multiplier = 50^2
            elif task.location is not None and task.priority == 2:
                multiplier = 50
            elif task.location is not None and task.priority == 1:
                multiplier = 1
            total_priority += task.priority * multiplier
        return total_priority / len(self.tasks)

def create_initial_population(task_list, population_size):
    return [Chromosome(random.sample(task_list, len(task_list))) for _ in range(population_size)]

def crossover(parent1, parent2):
    child_tasks = []

    for task in parent1.tasks:
        # Include tasks from parent1 if the priority is higher or the task is not in child_tasks
        if task not in child_tasks or task.priority > child_tasks[child_tasks.index(task)].priority:
            child_tasks.append(task)
        else:
            # Include tasks from parent2 if the priority is higher and not already in child_tasks
            parent2_tasks = [t for t in parent2.tasks if t not in child_tasks]
            higher_priority_tasks = [t for t in parent2_tasks if t.priority > task.priority]

            if higher_priority_tasks:
                child_tasks.append(random.choice(higher_priority_tasks))

    return Chromosome(child_tasks)

def mutate(chromosome):
    mutated_chromosome = chromosome.tasks.copy()

    # Skip mutation if the length is less than 2
    if len(mutated_chromosome) < 2:
        return Chromosome(mutated_chromosome)

    idx1, idx2 = random.sample(range(len(mutated_chromosome)), 2)
    mutated_chromosome[idx1], mutated_chromosome[idx2] = mutated_chromosome[idx2], mutated_chromosome[idx1]

    # Check if the mutated task has an entered location, and if it does, revert to the original task
    if mutated_chromosome[idx1].location is not None:
        mutated_chromosome[idx1] = chromosome.tasks[idx1]

    return Chromosome(mutated_chromosome)


def is_task_overlap(task1, task2):
    return task1.start_time < task2.end_time and task1.end_time > task2.start_time

def is_gap_between_tasks(task1, task2):
    return task2.start_time - task1.end_time > 0

def assign_locations(chromosome):
    machine_assignments = {}
    tasks_sorted_by_start_time = sorted(chromosome.tasks, key=lambda x: x.start_time)

    for task in tasks_sorted_by_start_time:
        candidate_machines = [machine for machine, last_task_end_time in machine_assignments.items()
                              if not is_task_overlap(task, last_task_end_time) and is_gap_between_tasks(last_task_end_time, task)]

        if candidate_machines:
            assigned_machine = random.choice(candidate_machines)
        elif task.location is not None:
            continue
        else:
            available_machines = set(range(1, 6)) - set(machine_assignments.keys())

            print(f"Task {task.name} available machines: {available_machines}")

            if available_machines:
                assigned_machine = random.choice(list(available_machines))
            else:
                assigned_machine = None  # Assign None when there are no available machines

        machine_assignments[assigned_machine] = task
        task.location = f"Machine{assigned_machine}" if assigned_machine is not None else None

# Replace the elite selection with tournament selection
def select_elite(population, elite_size):
    elites = []
    for _ in range(elite_size):
        tournament_size = min(3, len(population))  # Adjust the tournament size as needed
        tournament = random.sample(population, tournament_size)
        winner = max(tournament, key=lambda x: x.fitness)
        elites.append(winner)
    return elites

# Update the genetic_algorithm function to use the new elite selection
def genetic_algorithm(task_list, population_size, generations):
    population = create_initial_population(task_list, population_size)

    for generation in range(generations):
        population.sort(key=lambda x: x.fitness, reverse=True)
        elite = select_elite(population, 2)
        offspring = []

        for _ in range(population_size - 2):
            parent1 = random.choice(population)
            parent2 = random.choice(population)
            child = crossover(parent1, parent2)
            if random.random() < 0.1:  # Mutation probability
                child = mutate(child)
            assign_locations(child)  # Assign locations to the child
            offspring.append(child)

        population = elite + offspring

    return max(population, key=lambda x: x.fitness)


if __name__ == "__main__":
    tasks = [
        Task("Task1", start_time=0, end_time=3, priority=4, location='Machine1'),
        Task("Task2", start_time=2, end_time=7, priority=2),
        Task("Task3", start_time=5, end_time=7, priority=1),
        Task("Task4", start_time=8, end_time=12, priority=4),
        Task("Task5", start_time=1, end_time=5, priority=4),
        Task("Task6", start_time=6, end_time=10, priority=3),
        Task("Task7", start_time=2, end_time=6, priority=2),
        Task("Task8", start_time=4, end_time=9, priority=1),
        Task("Task9", start_time=9, end_time=12, priority=4),
        Task("Task10", start_time=1, end_time=4, priority=3),
        Task("Task11", start_time=5, end_time=9, priority=2),
        Task("Task12", start_time=3, end_time=8, priority=1),
        Task("Task13", start_time=7, end_time=11, priority=4),
        Task("Task14", start_time=10, end_time=15, priority=4),
        Task("Task15", start_time=2, end_time=5, priority=3),
        Task("Task16", start_time=6, end_time=9, priority=2),
        Task("Task17", start_time=4, end_time=7, priority=1),
        Task("Task18", start_time=8, end_time=11, priority=4),
        Task("Task19", start_time=1, end_time=6, priority=4),
        Task("Task20", start_time=3, end_time=8, priority=3),
    ]
    tasks = sorted(tasks, key=lambda x: x.priority, reverse=True)
    population_size = 40
    generations = 50

    result = genetic_algorithm(tasks, population_size, generations)

    print("Optimal Schedule:")
    for task in tasks:
        scheduled_task = next((t for t in result.tasks if t.name == task.name), None)
        if scheduled_task is not None and scheduled_task.location is not None:
            print(f"{scheduled_task.name} (Start Time: {scheduled_task.start_time}, End Time: {scheduled_task.end_time}, Priority: {scheduled_task.priority}, Location: {scheduled_task.location})")
        else:
            print(f"{task.name} not scheduled")
