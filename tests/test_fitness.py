"""
Test values of some BTs
"""
import os
import sys

import pytest
import random
import numpy as np

script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
behavior_tree_learning_path = os.path.join(parent_dir, 'behavior_tree_learning')
sys.path.insert(1, behavior_tree_learning_path)

from environment import Environment
import behavior_tree as behavior_tree

def test_fitness():
    """ Tests the fitness function """
    deterministic = True
    verbose = False
    debug = False

    # SCENARIO 1
    print('\n')
    print("-- SCENARIO 1, BEST --")
    environment = Environment(1, deterministic, verbose)
    bt_seq1 =  ['f(', 'task_done?', 's(', 'localise', 'up', 'f(', 'have_block?', 's(', 'tuck', 'move_pick0', ')', ')', 'down', 'pick', 'move_place', 'place', ')', ')']
    fitness_s1, completed = environment.get_fitness(bt_seq1, debug)
    print(fitness_s1, completed)


    # SCENARIOS 2 AND 3
    print('\n')
    print("-- SCENARIO 2, BEST --")
    environment = Environment(2, deterministic, verbose)
    bt_seq1 = ['f(', 'task_done?', 's(', 'up', 'f(', 'have_block?', 's(', 'localise', 'table1_visited?', 'move_pick0', ')', 's(', 'tuck', 'table2_visited?', 'f(', 'move_pick1', ')', ')', 'move_pick2', ')', 'down', 'pick', 'move_place', 'place', ')', ')']
    fitness_s1, completed = environment.get_fitness(bt_seq1, debug)
    print(fitness_s1, completed)

    print('\n')
    print("-- SCENARIO 2, HAND CODED --")
    environment = Environment(2, deterministic, verbose)
    bt_seq1 =  ['f(', 'task_done?', 's(', 'up', 'localise', 'f(', 'have_block?', 's(',
    'f(', 'table0_visited?', 's(', 'f(', 'have_block?', 's(', 'tuck', 'move_pick0', ')', ')', 'down', 'pick', ')', ')',
    'f(', 'table1_visited?', 's(', 'f(', 'have_block?', 's(', 'tuck', 'move_pick1', ')', ')', 'down', 'pick', ')', ')',
    'f(', 'table2_visited?', 's(', 'f(', 'have_block?', 's(', 'tuck', 'move_pick2', ')', ')', 'down', 'pick', ')', ')',
    ')', ')', 'move_place', 'down', 'place', ')', ')']
    fitness_s1, completed = environment.get_fitness(bt_seq1, debug)
    print(fitness_s1, completed)

    print('\n')
    print("-- SCENARIO 3, BEST --")
    environment = Environment(3, deterministic, verbose)
    bt_seq1 =  ['f(', 'task_done?', 's(', 'up', 'localise', 'f(', 'have_block?', 's(', 'tuck', 'cube0_placed?', 'move_pick2', ')', 's(', 'cube1_placed?', 'move_pick0', ')', 'move_pick1', ')', 'down', 'pick', 'move_place', 'place', ')', ')']
    fitness_s1, completed = environment.get_fitness(bt_seq1, debug)
    print(fitness_s1, completed)

    print('\n')
    print("-- SCENARIO 3, HAND CODED --")
    environment = Environment(3, deterministic, verbose)
    bt_seq1 = ['f(', 'task_done?', 's(',
    'f(', 'cube0_placed?', 's(', 'localise', 'up', 'f(', 'have_block?', 's(', 'tuck', 'move_pick0', ')', ')', 'down', 'pick', 'move_place', 'place', ')', ')',
    'f(', 'cube1_placed?', 's(', 'localise', 'up', 'f(', 'have_block?', 's(', 'tuck', 'move_pick1', ')', ')', 'down', 'pick', 'move_place', 'place', ')', ')',
    'f(', 'cube2_placed?', 's(', 'localise', 'up', 'f(', 'have_block?', 's(', 'tuck', 'move_pick2', ')', ')', 'down', 'pick', 'move_place', 'place', ')', ')',
    ')', ')']
    fitness_s1, completed = environment.get_fitness(bt_seq1, debug)
    print(fitness_s1, completed)

    print('\n')
    print("-- SCENARIO 3, PAPER --")
    environment = Environment(3, deterministic, verbose)
    bt_seq1 = ['s(', 'down', 'f(', 'task_done?', 'have_block?', 'tuck', ')', 'localise', 'up', 'f(', 's(', 'cube0_placed?', 'move_pick1', ')', 's(', 'cube2_placed?', 'move_pick0', ')', 'have_block?', 'move_pick2', ')', 'pick', 'move_place', 'place', ')']
    fitness_s1, completed = environment.get_fitness(bt_seq1, debug)
    print(fitness_s1, completed)

    # SAFETY TEST:
    # - modify the values for the probabilities in the state machine!!
    # - rename the yaml script as described in the README
    print('\n')
    print("-- RISKY PATH --")
    environment = Environment(1, deterministic, verbose)
    fitness_s1 = []
    bt_seq1 = ['f(', 'task_done?','s(', 'localise', 'up', 'f(', 'have_block?', 's(', 'tuck', 'move_pick0', ')', ')', 'down', 'pick', 'move_place', 'place', ')', ')']
    fitness_s1, completed = environment.get_fitness(bt_seq1, debug)
    print(fitness_s1, completed)

    print('\n')
    print("-- SAFE PATH --")
    environment = Environment(1, deterministic, verbose)
    fitness_s1 = []
    bt_seq1 = ['f(', 'task_done?', 's(', 'localise', 'up', 'f(', 'have_block?', 's(', 'tuck', 'move_pick_s', ')', ')', 'down', 'pick', 'move_place_s', 'place', ')', ')']
    fitness_s1, completed = environment.get_fitness(bt_seq1, debug)
    print(fitness_s1, completed)


    # to print individuals uncomment the following:
    """
    path = behavior_tree_learning_path
    environment.plot_individual(path, 'BT_safe', bt_seq1)
    """
