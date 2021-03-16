#!/usr/bin/env python3
# pylint: disable=global-at-module-level, too-many-instance-attributes
"""
A genetic programming algorithm with many possible settings
"""
import random
from enum import Enum, auto
from dataclasses import dataclass
from statistics import mean
import numpy as np

from hash_table import HashTable
import logplot as logplot

#Below are imports that can be changed to run agpinst different environments etc.
import gp_bt_interface as gp_interface

global COMPLETED
global INDIVIDUAL

class SelectionMethods(Enum):
    """ Enum class for selection methods """
    ELITISM = auto()
    TOURNAMENT = auto()
    RANK = auto()
    RANDOM = auto()
    ALL = auto()

@dataclass
class GpParameters:
    """ Data class for parameters for the GP algorithm """
    ind_start_length: int = 5                              #Start length of initial genomes
    n_population: int = 8                                  #Number of individuals in population
    f_crossover: float = 0.5                               #Fraction of parent pool selected for crossover
    n_offspring_crossover: int = 1                         #Number of offspring from crossover per parent
    f_mutation: float = 0.5                                #Fraction of parent pool selected for mutation
    n_offspring_mutation: int = 1                          #Number of offspring from mutation per parent
    parent_selection: int = SelectionMethods.TOURNAMENT    #Selection method for parents
    survivor_selection: int = SelectionMethods.TOURNAMENT  #Selection method for survival
    f_elites: float = 0.1                                  #Fraction of population that survive as elites
    f_parents: float = 1                                   #Fraction of parents that may survive to next generation
    mutate_co_offspring: bool = False                      #Offspring from crossover may also be mutated
    mutate_co_parents: bool = False                        #Parents for crossover may also be mutated
    mutation_p_add: float = 0.4                            #Probability of mutation adding a gene
    mutation_p_delete: float = 0.3                         #Probability of mutation deleting a gene
    allow_identical: bool = False                          #Offspring may be identical to any parent in prev generation
    plot: bool = True                                      #Plot fitness
    n_generations: int = 100                               #Number of generations
    hash_table_size: int = 100000                          #Size of hash table
    rerun_fitness: int = 1                                 #0-run only once, 1-according to prob, 2-always
    verbose: bool = False                                  #Extra prints
    log_name: str = '1'                                    #Name of log for folder and file handling
    fig_best: bool = True                                  #Save final best individual as figure
    fig_last_gen: bool = False                             #Save figures of entire last generation

def set_seeds(seed):
    """
    Sets random seeds for random number generators
    """
    random.seed(seed)
    np.random.seed(seed)

def create_population(population_size, genome_length):
    """
    Creates an initial random population
    """
    new_population = []
    max_attempts = 100

    for _ in range(population_size):
        individual = []
        attempts = 0

        while attempts < max_attempts:
            individual = gp_interface.random_genome(genome_length)
            if individual != [] and individual not in new_population:
                new_population.append(individual)
                break
            attempts += 1

    return new_population

def mutation(population, parents, gp_par):
    """
    Generate offspring by mutating a gene
    """
    mutated_population = []
    max_attempts = 100

    for parent in parents:
        for _ in range(gp_par.n_offspring_mutation):
            mutated_individual = []
            attempts = 0
            while attempts < max_attempts:
                mutated_individual = gp_interface.mutate_gene(population[parent], \
                                                              gp_par.mutation_p_add, \
                                                              gp_par.mutation_p_delete)
                if mutated_individual != [] and (gp_par.allow_identical or mutated_individual not in population):
                    mutated_population.append(mutated_individual)
                    break
                attempts += 1

    return mutated_population

def crossover(population, parents, gp_par):
    """
    Generates offspring by crossovers
    """

    if len(parents) % 2 != 0:
        raise ValueError("Number of parents for crossover must be even number")

    crossover_offspring = []
    max_attempts = 100

    for _ in range(gp_par.n_offspring_crossover):
        unused_parents = list(parents)
        attempts = 0

        while len(unused_parents) >= 2 and attempts < max_attempts:
            crossover_parents = random.sample(range(len(unused_parents)), 2)
            parent1 = unused_parents[int(crossover_parents[0])]
            parent2 = unused_parents[int(crossover_parents[1])]
            offspring1, offspring2 = gp_interface.crossover_genome(population[parent1], population[parent2])

            if offspring1 != [] and offspring2 != [] and \
                (gp_par.allow_identical or (offspring1 not in population and offspring2 not in population)):
                crossover_offspring.append(offspring1)
                crossover_offspring.append(offspring2)
                unused_parents.pop(crossover_parents[0])
                if crossover_parents[0] < crossover_parents[1]:
                    crossover_parents[1] -= 1
                unused_parents.pop(crossover_parents[1])
                attempts = 0
            else:
                attempts += 1

        if attempts == max_attempts and len(unused_parents) > 0 and \
            gp_par.n_offspring_mutation <= 1 and gp_par.n_offspring_crossover <= 1:
            #Fill up with mutation in case we can't find enough good crossovers
            crossover_offspring += mutation(population, unused_parents, gp_par)

    return crossover_offspring

def rerun_probability(n_runs):
    """
    Calculates a probability for running another episode with the same genome
    """
    if n_runs <= 0:
        return 1
    else:
        return 1 / n_runs**2

def get_fitness(individual, hash_table, environment, rerun=0):
    """
    Gets fitness from hash table if possible, otherwise gets it from simulation
    rerun = 0 means never rerun
    rerun = 1 means rerun with diminishing probability
    rerun = 2 means rerun always
    """
    global COMPLETED
    global INDIVIDUAL

    values = hash_table.find(individual)

    if values is None or rerun == 2 or (rerun == 1 and random.random() < rerun_probability(len(values))):
        fitness, done = environment.get_fitness(individual)
        hash_table.insert(individual, fitness)
        if done:
            INDIVIDUAL = individual
            COMPLETED = True

        if values is None:
            values = [fitness]

    return mean(values)

def crossover_parent_selection(population, fitness, gp_par):
    """
    Select parents for crossover. Returns indices of parents.
    """
    n_parents_crossover = int(round(gp_par.f_crossover * gp_par.n_population))
    if n_parents_crossover <= 0:
        return []
    return selection(range(len(population)), fitness, n_parents_crossover, gp_par.parent_selection)

def mutation_parent_selection(population, fitness, crossover_parents, crossover_offspring, gp_par):
    """
    Select parents for crossover
    Input fitness contains fitness for crossover offspring after fitness for the rest of the population
    Input population does not contain crossover offspring
    Returns indices of parents.
    """
    mutable_population = population[:]
    mutable_fitness = fitness[:]

    if not gp_par.mutate_co_parents:
        crossover_parents.sort(reverse=True)
        for i in crossover_parents:
            mutable_population.pop(i)
            mutable_fitness.pop(i)
    if gp_par.mutate_co_offspring:
        mutable_population += crossover_offspring
    else:
        mutable_fitness = mutable_fitness[:len(population)]

    n_parents_mutation = int(round(gp_par.f_mutation * gp_par.n_population))
    if n_parents_mutation <= 0:
        return []

    return selection(range(len(mutable_population)), fitness, n_parents_mutation, gp_par.parent_selection)

def survivor_selection(population, fitness, crossover_offspring, mutated_offspring, gp_par):
    """
    Select survivors for next generation
    """
    selectable = []
    selectable_fitness = []
    survivors = []
    survivor_fitness = []

    #Pick out selectable parents using elitism.
    n_parents = int(round(gp_par.f_parents * gp_par.n_population))
    if n_parents > 0:
        parents = elite_selection(range(len(population)), fitness[:len(population)], n_parents)
        for i in parents:
            selectable.append(population[i])
            selectable_fitness.append(fitness[i])

    #Add offspring
    selectable += crossover_offspring + mutated_offspring
    selectable_fitness += fitness[len(population):]

    #Pick out elites
    n_elites = int(round(gp_par.f_elites * gp_par.n_population))
    if n_elites > 0:
        elites = elite_selection(range(len(selectable)), selectable_fitness, n_elites)
        elites.sort(reverse=True)
        for i in elites:
            survivors.append(selectable[i])
            survivor_fitness.append(selectable_fitness[i])
            selectable.pop(i)
            selectable_fitness.pop(i)

    n_to_select = gp_par.n_population - len(survivors)
    selected = selection(range(len(selectable)), selectable_fitness, n_to_select, gp_par.survivor_selection)

    for i in selected:
        survivors.append(selectable[i])
        survivor_fitness.append(selectable_fitness[i])

    return survivors, survivor_fitness

def selection(population, fitness, n_selected, selection_method):
    """
    Select individuals from population
    """
    if selection_method == SelectionMethods.ELITISM:
        selected = elite_selection(population, fitness, n_selected)
    elif selection_method == SelectionMethods.TOURNAMENT:
        selected = tournament_selection(population, fitness, n_selected)
    elif selection_method == SelectionMethods.RANK:
        selected = rank_selection(population, fitness, n_selected)
    elif selection_method == SelectionMethods.RANDOM:
        selected = random.sample(population, n_selected)
    elif selection_method == SelectionMethods.ALL:
        selected = population
    else:
        raise Exception('Invalid selection method')

    return selected

def elite_selection(population, fitness, n_elites):
    """
    Elite selection from population
    """
    sorted_population = sorted(zip(fitness, population), reverse=True)

    return [x for _, x in sorted_population[:n_elites]]

def tournament_selection(population, fitness, n_winners):
    """
    Tournament selection.
    """
    tournament_size = n_winners
    while tournament_size < len(population):
        tournament_size *= 2

    tournament_population = list(zip(fitness, population))
    random.shuffle(tournament_population)

    for i in range(tournament_size - len(population)):
        #Add dummies to make sure we have a full tournament
        tournament_population.insert(i * 2, (-float("inf"), []))

    winner_fitness, winners = [list(x) for x in zip(*tournament_population)]
    while len(winners) > n_winners:
        for i in range(0, int(len(winners) / 2)):
            if winner_fitness[i] < winner_fitness[i+1]:
                winner_fitness.pop(i)
                winners.pop(i)
            else:
                winner_fitness.pop(i + 1)
                winners.pop(i + 1)

    return winners

def rank_selection(population, fitness, n_selected):
    """
    Rank proportional selection
    Probabilities for each individual are scaled linearly according to rank
    such that the highest ranked individual get n_ranks as weight
    and the lowest ranked individual gets 1. The weights are then scaled so
    that they sum to 1.
    """
    sorted_population = sorted(zip(fitness, population), reverse=True)
    _, sorted_indices = [list(x) for x in zip(*sorted_population)]
    n_ranks = len(sorted_indices)
    p = np.linspace(2 / (n_ranks + 1), 2 / (n_ranks * (n_ranks + 1)), n_ranks)
    return list(np.random.choice(sorted_indices, size=n_selected, replace=False, p=p))

def print_population(population, fitness, generation):
    """
    Prints information about a population
    """
    print("Generation: ", generation)
    for i in range(len(population)):
        print(population[i])
        print("Fitness: ", fitness[i])
    best = np.argmax(fitness)
    print("Best individual: ", best)
    print(population[best])



def run(environment, gp_par, hotstart=False, hotstart_population=None, baseline=None):
    """
    Runs the genetic algorithm
    """
    global COMPLETED
    global INDIVIDUAL
    COMPLETED = False
    INDIVIDUAL = None

    hash_table = HashTable(gp_par.hash_table_size, gp_par.log_name)

    if hotstart:
        population = hotstart_population.copy()
        hash_table.load()
    else:
        population = create_population(gp_par.n_population, gp_par.ind_start_length)
        logplot.clear_logs(gp_par.log_name)

    if baseline is not None:
        population[0] = baseline

    #log_video_path = '/home/matteo/Documents/behavior-tree-learning/logs/log_' + str(gp_par.log_name) + '/BTs_for_' + str(gp_par.log_name)

    fitness = []
    best_fitness = []
    n_episodes = []
    for individual in population:
        fitness.append(get_fitness(individual, hash_table, environment, rerun=0))

    best_fitness.append(max(fitness))
    n_episodes.append(hash_table.n_values)

    if gp_par.verbose:
        print_population(population, fitness, 0)

    print("Generation: ", 0, " Best fitness: ", best_fitness)

    # for video purpose
    """
    with open(log_video_path, "w") as f:
        f.writelines("Initial Generation:\n")
        f.writelines(str(population))
    f.close()
    """

    logplot.log_fitness(gp_par.log_name, fitness)
    logplot.log_population(gp_par.log_name, population)

    for generation in range(1, gp_par.n_generations):
        if baseline is not None and not baseline in population:
            population.append(baseline) #Make sure we are always able to source from baseline

        if generation > 1:
            fitness = []
            for individual in population:
                fitness.append(get_fitness(individual, hash_table, environment, gp_par.rerun_fitness))

        co_parents = crossover_parent_selection(population, fitness, gp_par)
        co_offspring = crossover(population, co_parents, gp_par)
        #print("Offspring:" + str(co_offspring))
        for offspring in co_offspring:
            fitness.append(get_fitness(offspring, hash_table, environment, gp_par.rerun_fitness))

        mutation_parents = mutation_parent_selection(population, fitness, co_parents, co_offspring, gp_par)
        #print("Mutation Parents:" + str(mutation_parents))
        mutated_offspring = mutation(population + co_offspring, mutation_parents, gp_par)
        for offspring in mutated_offspring:
            fitness.append(get_fitness(offspring, hash_table, environment, gp_par.rerun_fitness))

        population, fitness = survivor_selection(population, fitness, co_offspring, mutated_offspring, gp_par)

        best_fitness.append(max(fitness))
        n_episodes.append(hash_table.n_values)

        best_individual = selection(population, fitness, 1, SelectionMethods.ELITISM)[0]

        logplot.log_fitness(gp_par.log_name, fitness)
        logplot.log_population(gp_par.log_name, population)

        # for video purpose
        """
        if max(fitness) > best_fitness[-2]:
            with open(log_video_path, "a") as f:
                f.writelines("\nGeneration: " + str(generation) + "\n")
                f.writelines(str(max(fitness)) + ", " + str(best_individual))
            f.close()
        """

        #print_population(population, fitness, generation)
        #print(INDIVIDUAL)

        print("Generation: ", generation, "Best fitness: ", best_fitness[generation])
        print("Best individual: " + str(best_individual))
        print("Completed? " + str(COMPLETED))


    hash_table.write_table()
    best_individual = selection(population, fitness, 1, SelectionMethods.ELITISM)[0]
    logplot.log_best_individual(gp_par.log_name, best_individual)
    logplot.log_best_fitness(gp_par.log_name, best_fitness)
    logplot.log_n_episodes(gp_par.log_name, n_episodes)
    logplot.log_settings(gp_par.log_name, gp_par)

    if gp_par.plot:
        logplot.plot_fitness(gp_par.log_name, best_fitness, n_episodes)
    if gp_par.fig_best:
        environment.plot_individual(logplot.get_log_folder(gp_par.log_name), 'best individual', selection(population, fitness, 1, SelectionMethods.ELITISM)[0])
    if gp_par.fig_last_gen:
        for i in range(gp_par.n_population):
            environment.plot_individual(logplot.get_log_folder(gp_par.log_name), 'individual_' + str(i), population[i])

    return population, fitness, best_fitness, best_individual
