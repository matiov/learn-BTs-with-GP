#!/usr/bin/env python3
"""
A simple simulation environment for testing duplo handling.
All environments must contain a get_fitness(individual) function
that returns a fitness value and a plot_individual() function that
returns nothing but saves a graphical representation of the individual
"""
import os
import sys

import behavior_tree as behavior_tree
from py_trees_interface import PyTree
import behaviors as behaviors
import state_machine as sm
import cost_function


class Environment:
    """ Class defining the environment in which the individual operates """

    def __init__(self, scenario, deterministic=False, verbose=False):
        self.scenario = scenario
        self.deterministic = deterministic
        self.verbose = verbose

        # Load setting file with the behaviors specifications
        script_dir = os.path.dirname(__file__)
        parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
        file_scenario = 'BT_SCENARIO_' + str(self.scenario) + '.yml'
        settings_path = os.path.join(parent_dir, file_scenario)
        behavior_tree.load_settings_from_file(settings_path)

    def get_fitness(self, string, debug=False):
        """ Run the simulation and return the fitness """

        if self.scenario == 2:
            # in this case we run the same BT against the state machine in 3 different setups
            # every setup features a different spawn pose for the cube
            fitness = 0
            performance = 0
            completed = False
            for i in range(3):
                state_machine = sm.StateMachine(self.scenario, self.deterministic, self.verbose, pose_id=i)
                behavior_tree = PyTree(string[:], behaviors=behaviors, state_machine=state_machine)

                # run the Behavior Tree
                ticks = behavior_tree.tick_bt()

                cost, output = cost_function.compute_cost(state_machine, behavior_tree, ticks, debug=debug)

                fitness += -cost/3.0
                performance += int(output)

            if performance == 3:
                completed = True

        else:
            state_machine = sm.StateMachine(self.scenario, self.deterministic, self.verbose)
            behavior_tree = PyTree(string[:], behaviors=behaviors, state_machine=state_machine)

            # run the Behavior Tree
            ticks = behavior_tree.tick_bt()

            cost, completed = cost_function.compute_cost(state_machine, behavior_tree, ticks, debug=debug)
            fitness = -cost

        return fitness, completed

    def plot_individual(self, path, plot_name, individual):
        """ Saves a graphical representation of the individual """
        pytree = PyTree(individual[:], behaviors=behaviors)
        pytree.save_fig(path, name=plot_name)
