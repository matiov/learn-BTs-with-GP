#!/usr/bin/env python3
# pylint: disable=global-at-module-level, global-statement, global-variable-undefined
"""
Task dependent cost function
"""

from dataclasses import dataclass
import state_machine as sm

@dataclass
class Coefficients:
    # BT structure:
    depth: float = 0.0
    length: float = 0.5
    time: float = 0.1
    failure: float = 0.0
    # Task steps:
    task_completion: int = 300
    subtask: int = 100
    pick: int = 50
    # Gradient:
    cube_dist: int = 10
    localization: int = 1
    distance_robot_cube: int = 2
    robot_dist: int = 0
    min_distance_robot_cube: int = 0
    min_distance_cube_goal: int = 0

def compute_cost(state_machine, behavior_tree, ticks, debug=False):
    """ Retrieve values and compute cost """

    completed = False

    coeff = Coefficients()

    depth = behavior_tree.depth
    length = behavior_tree.length

    cube_dist = sum(state_machine.feedback[sm.Feedback.CUBE_DISTANCE])
    min_cube_dist = sum(state_machine.feedback[sm.Feedback.MIN_CUBE_DISTANCE])
    robot_cube_dist = sum(state_machine.feedback[sm.Feedback.ROBOT_CUBE_DISTANCE])
    min_rc_dist = sum(state_machine.feedback[sm.Feedback.MIN_RC_DISTANCE])

    robot_dist = state_machine.feedback[sm.Feedback.ROBOT_DISTANCE]
    loc_error = state_machine.feedback[sm.Feedback.LOCALIZATION_ERROR]
    time = state_machine.feedback[sm.Feedback.ELAPSED_TIME]
    p_failure = state_machine.feedback[sm.Feedback.FAILURE_PB]

    cost = float(coeff.length*length +\
           coeff.depth*depth +\
           coeff.cube_dist*cube_dist**2 +\
           coeff.localization*loc_error**2 +\
           coeff.distance_robot_cube*robot_cube_dist**2 +\
           coeff.min_distance_cube_goal*min_cube_dist**2 +\
           coeff.min_distance_robot_cube*min_rc_dist**2 +\
           coeff.robot_dist*robot_dist**2 +\
           coeff.time*time) +\
           coeff.failure*p_failure


    if cube_dist == 0.0:
        completed = True
    else:
        # the task is not completed!
        cost += coeff.task_completion
        for i in range(state_machine.cubes):
            if state_machine.feedback[sm.Feedback.CUBE_DISTANCE][i] == 0.0:
                cost -= coeff.subtask
            if state_machine.current[sm.State.HAS_CUBE] and state_machine.current[sm.State.CUBE_ID] == i:
                cost -= coeff.pick

    if debug:
        print("\n")
        print("Ticks: " + str(ticks))
        print("Cube pose: " + str(state_machine.feedback[sm.Feedback.CUBE]))
        print("Robot pose: " + str(state_machine.feedback[sm.Feedback.AMCL]))
        print("State pose: " + str(state_machine.current[sm.State.POSE]))
        print("\n")
        print("Cube distance from goal: " + str(cube_dist))
        print("Contribution: " + str(coeff.cube_dist*cube_dist**2))
        print("Min cube distance: " + str(min_cube_dist))
        print("Contribution: " + str(coeff.min_distance_cube_goal*min_cube_dist**2))
        print("Robot distance from cube: " + str(robot_cube_dist))
        print("Contribution: " + str(coeff.distance_robot_cube*robot_cube_dist**2))
        print("Min robot distance: " + str(min_rc_dist))
        print("Contribution: " + str(coeff.min_distance_robot_cube*min_rc_dist**2))
        print("Robot distance from goal: " + str(robot_dist))
        print("Contribution: " + str(coeff.robot_dist*robot_dist**2))
        print("Localisation Error: " + str(loc_error))
        print("Contribution: " + str(coeff.localization*loc_error**2))
        print("Behavior Tree: L " + str(length) + ", D " + str(depth))
        print("Contribution: " + str(coeff.length*length + coeff.depth*depth))
        print("Elapsed Time: " + str(time))
        print("Contribution: " + str(coeff.time*time))
        print("Failure Probability: " + str(p_failure))
        print("Contribution: " + str(coeff.failure*p_failure))
        print("Total Cost: " + str(cost))
        print("\n")

    return cost, completed
