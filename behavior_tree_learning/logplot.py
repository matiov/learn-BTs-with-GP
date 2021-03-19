#!/usr/bin/env python3
# pylint: disable=too-many-instance-attributes
"""
Handling of logs and plots for learning
"""
import os
import sys

script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.insert(1, parent_dir)

import shutil
import pickle
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

def open_file(path, mode):
    """
    Attempts to open file at path.
    Tried up to max_attempts times because of intermittent permission errors on windows
    """
    max_attempts = 100
    f = None
    for _ in range(max_attempts): # pragma: no branch
        try:
            f = open(path, mode)
        except PermissionError: # pragma: no cover
            continue
        break
    return f

def make_directory(path):
    """
    Attempts to create directory at path.
    Tried up to max_attempts times because of intermittent permission errors on windows
    """
    max_attempts = 100
    for _ in range(max_attempts): # pragma: no branch
        try:
            os.mkdir(path)
        except PermissionError: # pragma: no cover
            continue
        break

def get_log_folder(log_name):
    """ Returns log folder as string """
    return parent_dir + '/logs/log_' + log_name

def clear_logs(log_name):
    """ Clears previous log folders of same same """

    log_folder = get_log_folder(log_name)
    try:
        shutil.rmtree(log_folder)
    except FileNotFoundError: # pragma: no cover
        pass

    make_directory(log_folder)
    fitness_log_path = log_folder + '/fitness_log.txt'
    population_log_path = log_folder + '/population_log.txt'
    open(fitness_log_path, "x")
    open(population_log_path, "x")

def log_best_individual(log_name, best_individual):
    """ Saves the best individual """
    with open_file(get_log_folder(log_name) + '/best_individual.pickle', 'wb') as f:
        pickle.dump(best_individual, f)

def log_fitness(log_name, fitness):
    """ Logs fitness of all individuals """
    with open_file(get_log_folder(log_name) + '/fitness_log.txt', 'a') as f:
        f.write("%s\n" % fitness)

def log_best_fitness(log_name, best_fitness):
    """ Logs best fitness of each generation """
    with open_file(get_log_folder(log_name) + '/best_fitness_log.pickle', 'wb') as f:
        pickle.dump(best_fitness, f)

def log_n_episodes(log_name, n_episodes):
    """ Logs number of episodes """
    with open_file(get_log_folder(log_name) + '/n_episodes_log.pickle', 'wb') as f:
        pickle.dump(n_episodes, f)

def log_population(log_name, population):
    """ Logs full population of the generation"""
    with open_file(get_log_folder(log_name) + '/population_log.txt', 'a') as f:
        f.write("%s\n" % population)

def log_settings(log_name, settings):
    """ Logs settings used for the run """
    with open_file(get_log_folder(log_name) + '/settings.txt', 'a') as f:
        for key, value in vars(settings).items():
            f.write(key + ' ' + str(value) + '\n')

def get_best_fitness(log_name):
    """ Gets the best fitness list from the given log """
    with open_file(get_log_folder(log_name) + '/best_fitness_log.pickle', 'rb') as f:
        best_fitness = pickle.load(f)
    return best_fitness

def get_n_episodes(log_name):
    """ Gets the list of n_episodes from the given log """
    with open_file(get_log_folder(log_name) + '/n_episodes_log.pickle', 'rb') as f:
        n_episodes = pickle.load(f)
    return n_episodes

def get_last_line(file_name):
    """ Returns the last line of the given file """
    with open_file(file_name, 'rb') as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        last_line = f.readline().decode()
    return last_line

def get_last_population(log_name):
    """ Gets the last population list from the given log """
    return get_last_line(get_log_folder(log_name) + '/population_log.txt')

def get_last_fitness(log_name):
    """ Get the fitness list from the given log """
    return get_last_line(get_log_folder(log_name) + '/fitness_log.txt')

def get_best_individual(log_name):
    """ Return the best individual from the given log """
    with open_file(get_log_folder(log_name) + '/best_individual.pickle', 'rb') as f:
        best_individual = pickle.load(f)
    return best_individual

def plot_fitness(log_name, fitness, n_episodes=None):
    """
    Plots fitness over iterations or individuals
    """
    if n_episodes is not None:
        plt.plot(n_episodes, fitness)
        plt.xlabel("Episodes")
    else:
        plt.plot(fitness)
        plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.savefig(get_log_folder(log_name) + '/Fitness.svg')
    plt.close()

@dataclass
class PlotParameters:
    """ Data class for parameters for plotting """
    plot_mean: bool = True          #Plot the mean of the logs
    mean_color: str = 'b'           #Color for mean curve
    plot_std: bool = False          #Plot the standard deviation
    std_color: str = 'b'            #Color of the std fill
    plot_ind: bool = False          #Plot each individual log
    ind_color: str = 'aquamarine'   #Ind color
    legend_name: str = ''           #Legend name
    legend_fsize: float = 16.0      #Set font size of legend
    title: str = ''                 #Plot title
    title_fsize: float = 18.0       #Set font size of title
    xlabel: str = ''                #Label of x axis
    x_max: int = 0                  #Upper limit of x axis
    ylabel: str = ''                #Label of y axis
    label_fsize: float = 16.0       ##Set font size of axis labels
    extrapolate_y: bool = True      #Extrapolate y as constant to x_max
    plot_optimal: bool = True       #Plot optimal value as thin vertical line
    optimum: float = 0              #Optimal value to plot
    save_fig: bool = True           #Save figure. If false, more plots is possible.
    path: str = 'logs/plot.png'     #Path to save log

def plot_learning_curves(logs, parameters):
    """
    Plots mean and standard deviation of a number of logs in the same figure
    """
    fitness = []
    n_episodes = []
    for log_name in logs:
        fitness.append(get_best_fitness(log_name))

        n_episodes.append(get_n_episodes(log_name))

    fitness = np.array(fitness)
    n_episodes = np.array(n_episodes)

    n_logs = len(logs)
    startx = np.max(n_episodes[:, 0])
    endx = np.min(n_episodes[:, -1])
    if parameters.extrapolate_y:
        x = np.arange(startx, parameters.x_max + 1)
    else:
        x = np.arange(startx, endx + 1)
    y = np.zeros((len(x), n_logs))
    for i in range(0, n_logs):
        f = interpolate.interp1d(n_episodes[i, :], fitness[i, :], bounds_error=False)
        y[:, i] = f(x)
        if parameters.extrapolate_y:
            n_extrapolated = int(parameters.x_max - n_episodes[i, -1])
            if n_extrapolated > 0:
                left = y[:n_episodes[i, -1] - n_episodes[i, 0] + 1, i]
                y[:, i] = np.concatenate((left, np.full(n_extrapolated, left[-1])))
        if parameters.plot_ind:
            plt.plot(x, y[:, i], color=parameters.ind_color, linestyle='dashed', linewidth=1)

    y_mean = np.mean(y, axis=1)
    if parameters.plot_mean:
        plt.plot(x, y_mean, color=parameters.mean_color, label=parameters.legend_name)
    y_std = np.std(y, axis=1)
    if parameters.plot_std:
        plt.fill_between(x, y_mean - y_std, y_mean + y_std, alpha=.1, color=parameters.std_color)

    plt.legend(loc="lower right", prop={'size': parameters.legend_fsize})
    plt.xlabel(parameters.xlabel, fontsize=parameters.label_fsize)
    if parameters.x_max > 0:
        plt.xlim(0, parameters.x_max)
    plt.ylabel(parameters.ylabel, fontsize=parameters.label_fsize)
    plt.title(parameters.title, fontsize=parameters.title_fsize, wrap=True)
    if parameters.save_fig:
        if parameters.plot_optimal:
            plt.plot([0, parameters.x_max], \
                     [parameters.optimum, parameters.optimum], \
                     color='k', linestyle='dashed', linewidth=1)
        plt.savefig(parameters.path, format='svg', dpi=300)
        plt.close()
