#!/usr/bin/env python3
# pylint: disable=global-at-module-level, global-statement, global-variable-undefined, line-too-long
"""
State Machine Simulator
"""
import random
import math
from enum import IntEnum
from dataclasses import dataclass, field
from typing import List

class State(IntEnum):
    """
    Definition of a state in the State Machine Simulator
    """
    LOCALISED = 0
    HEAD = 1
    ARM = 2
    POSE = 3
    HAS_CUBE = 4
    CUBE_ID = 5
    VISITED = 6

class Feedback(IntEnum):
    """
    Feedback values for the fitness function
    """
    AMCL = 0                    # particle filter pose estimate (Augmented Monte Carlo Localization)
    CUBE = 1                    # cube pose
    CUBE_DISTANCE = 2           # distance of the cube from the goal
    MIN_CUBE_DISTANCE = 3       # min distance of the cube from the goal pose
    ROBOT_CUBE_DISTANCE = 4     # distance of the robot from the cube
    MIN_RC_DISTANCE = 5         # min distance of the robot from the cube
    ROBOT_DISTANCE = 6          # dstance of the robot to the place pose
    LOCALIZATION_ERROR = 7      # distance of the amcl estimate from the real robot pose
    ELAPSED_TIME = 8            # total time elapsed since the beginning of the simulation
    FAILURE_PB = 9              # sum of the probabilities of failure of the BT

@dataclass
class Poses:
    """
    Data class for parameters for the environment poses.
    Note that the poses are pre-defined because there is a one-to-one
    correspondance with the simulation environment in Gazebo (see paper)
    """
    spawn_pose: List[float] = field(default_factory=list)                # Spawn position of the robot
    pick_table0: List[float] = field(default_factory=list)               # Position the robot has to reach to pick the cube 0
    pick_table1: List[float] = field(default_factory=list)               # Position the robot has to reach to pick the cube 1
    pick_table2: List[float] = field(default_factory=list)               # Position the robot has to reach to pick the cube 2
    place_table: List[float] = field(default_factory=list)               # Position the robot has to reach to place the cube
    random_pose1: List[float] = field(default_factory=list)              # First random position attainable by the robot
    random_pose2: List[float] = field(default_factory=list)              # Second random position attainable by the robot
    random_pose3: List[float] = field(default_factory=list)              # Third random position attainable by the robot
    random_pose4: List[float] = field(default_factory=list)              # Fourth random position attainable by the robot
    random_pose5: List[float] = field(default_factory=list)              # Fifth random position attainable by the robot
    random_pose6: List[float] = field(default_factory=list)              # Sixth random position attainable by the robot
    random_pose7: List[float] = field(default_factory=list)              # Seventh random position attainable by the robot
    random_pose8: List[float] = field(default_factory=list)              # Eight random position attainable by the robot
    random_pose9: List[float] = field(default_factory=list)              # Ninth random position attainable by the robot
    origin: List[float] = field(default_factory=list)                    # World frame
    half_way: List[float] = field(default_factory=list)                  # Pose half way between pick and place tables
    amcl_init_pose: List[float] = field(default_factory=list)            # Initial estimated position of the robot (before localization)
    cubes_spawn_pose: List[float] = field(default_factory=list)          # List of the spawn poses for the cubes
    cube0_spawn_pose: List[float] = field(default_factory=list)          # Spawn position of the cube 0
    cube1_spawn_pose: List[float] = field(default_factory=list)          # Spawn position of the cube 1
    cube2_spawn_pose: List[float] = field(default_factory=list)          # Spawn position of the cube 2
    cube_goal_pose: List[float] = field(default_factory=list)            # Goal position of the cube

@dataclass
class SMParameters:
    """Data class for parameters for the state machine simulator """
    deterministic: bool = False                            # Probabilistic nature of the simulator (deterministic/probabilistic)
    fail_pick_probability: float = 0.2                     # Probability of a failure in Picking (Place transition)
    fail_place_probability: float = 0.1                    # Probability of a failure in Placing (Place transition)
    fail_tuck_probability: float = 0.0                     # Probability of a failure in Tucking (Tuck transition)
    fail_localization_probability: float = 0.2             # Probability of convergence failure of the AMCL particle filter (Loccalize transition)
    fail_navigation_probability: float = 0.0               # Probability of not reaching the correct pose (Pose transition)
    drop_probability: float = 0.05                         # Probability of dropping the cube during motion (Pose transition)
    lost_probability: float = 0.1                          # Probability of loosing the localization during motion (Pose transition)
    verbose: bool = False                                  # Extra prints

class StateMachine:
    """
    Class for handling the State Machine Simulator
    """
    def __init__(self, scenario, deterministic=False, verbose=False, pose_id=0):

        self.sm_par = SMParameters()
        self.sm_par.deterministic = deterministic
        self.sm_par.verbose = verbose

        self.poses = Poses()
        self.poses.cubes_spawn_pose = [[-1.13053, -6.65365, 0.8625], [-2.32, -11.07, 0.865], [-1.086, -0.545, 0.866]]

        # Create simulation scenario
        self.cubes = 1

        if scenario == 1:
            self.poses.cubes_spawn_pose = [self.poses.cubes_spawn_pose[0]]
            self.poses.cube0_spawn_pose += self.poses.cubes_spawn_pose[0]
        elif scenario == 2:
            self.poses.cube0_spawn_pose += self.poses.cubes_spawn_pose[pose_id]
            self.poses.cubes_spawn_pose = [self.poses.cube0_spawn_pose]
        elif scenario == 3:
            self.cubes = 3
            self.poses.cube0_spawn_pose += self.poses.cubes_spawn_pose[0]
            self.poses.cube1_spawn_pose += self.poses.cubes_spawn_pose[1]
            self.poses.cube2_spawn_pose += self.poses.cubes_spawn_pose[2]
        else:
            raise Exception('Simulation scenario not supported.')

        # robot related (2D)
        self.poses.spawn_pose += [2.40, -11.0]
        self.poses.pick_table0 += [-1.148, -6.1]
        self.poses.pick_table1 += [-2.32, -10.52]
        self.poses.pick_table2 += [-0.54, -0.545]
        self.poses.place_table += [2.6009, -1.7615]
        self.poses.random_pose1 += [-2.0, -9.0]
        self.poses.random_pose2 += [-4.0, -9.0]
        self.poses.random_pose3 += [2.0, 7.0]
        self.poses.random_pose4 += [-4.0, 0.0]
        self.poses.random_pose5 += [-3.0, -5.0]
        self.poses.random_pose6 += [3.0, -10.0]
        self.poses.random_pose7 += [-4.0, -12.0]
        self.poses.random_pose8 += [-3.0, -2.0]
        self.poses.random_pose9 += [4.0, 1.0]
        self.poses.origin += [0.0, 0.0]
        self.poses.amcl_init_pose += [-0.03343, -0.0321]

        # cube related (3D)
        self.poses.cube_goal_pose += [3.1509, -1.7615, 0.8625]

        #robot velocity
        self.velocity = 0.3

        self.current = [None]*(len(State))
        self.current[State.LOCALISED] = False
        self.current[State.HEAD] = "Down"
        self.current[State.ARM] = "Stretched"
        self.current[State.POSE] = self.poses.spawn_pose
        self.current[State.HAS_CUBE] = False
        self.current[State.CUBE_ID] = None
        self.current[State.VISITED] = [False, False, False]

        self.feedback = [None]*(len(Feedback))
        self.feedback[Feedback.AMCL] = list(self.poses.amcl_init_pose)
        self.feedback[Feedback.CUBE] = list(self.poses.cubes_spawn_pose)
        self.feedback[Feedback.CUBE_DISTANCE] = [None]*self.cubes
        self.feedback[Feedback.ROBOT_CUBE_DISTANCE] = [None]*self.cubes

        # Populate feedback lists with the values
        for i in range(self.cubes):
            self.feedback[Feedback.CUBE_DISTANCE][i] = distance(self.poses.cubes_spawn_pose[i], self.poses.cube_goal_pose)
            self.feedback[Feedback.ROBOT_CUBE_DISTANCE][i] = distance(self.poses.cubes_spawn_pose[i][0:2], self.poses.spawn_pose)

        self.feedback[Feedback.MIN_CUBE_DISTANCE] = list(self.feedback[Feedback.CUBE_DISTANCE])
        self.feedback[Feedback.MIN_RC_DISTANCE] = list(self.feedback[Feedback.ROBOT_CUBE_DISTANCE])
        self.feedback[Feedback.ROBOT_DISTANCE] = distance(self.poses.spawn_pose, self.poses.place_table)
        self.feedback[Feedback.LOCALIZATION_ERROR] = distance(self.poses.amcl_init_pose, self.poses.spawn_pose)
        self.feedback[Feedback.ELAPSED_TIME] = 0.0
        self.feedback[Feedback.FAILURE_PB] = 0.0

        self.manipulating = False
        self.moving = False

    def update_feedback(self):
        """ Update the Feedback state """
        # Update AMCL
        if self.current[State.LOCALISED]:
            self.feedback[Feedback.AMCL] = list(map(lambda x,y:x+y, self.current[State.POSE], [random.random()*0.1, random.random()*0.1]))
        else:
            # big error around last known pose
            self.feedback[Feedback.AMCL] = list(map(lambda x,y:x+y, self.feedback[Feedback.AMCL], [random.uniform(1.5, 2.5), random.uniform(1.5, 2.5)]))

        self.feedback[Feedback.LOCALIZATION_ERROR] = distance(self.feedback[Feedback.AMCL], self.current[State.POSE])

        angle = [0, 0]
        if self.current[State.POSE] == self.poses.spawn_pose:
            angle = [0, 1]
        elif self.current[State.POSE] == self.poses.pick_table0 or self.current[State.POSE] == self.poses.pick_table1:
            angle = [0, -1]
        elif self.current[State.POSE] == self.poses.pick_table2:
            angle = [-1, 0]
        elif self.current[State.POSE] == self.poses.place_table:
            angle = [1, 0]
        else:
            angle = [1, 0]

        if self.current[State.HAS_CUBE] and self.current[State.CUBE_ID] is not None:
            # x coordinate + 50cm (accounting to the robot in picking pose)
            self.feedback[Feedback.CUBE][self.current[State.CUBE_ID]][0] = float(self.current[State.POSE][0] + 0.3*angle[0]) + random.uniform(-0.1, 0.1)
            # y coordinate + 50cm (accounting to the robot in picking pose)
            self.feedback[Feedback.CUBE][self.current[State.CUBE_ID]][1] = float(self.current[State.POSE][1] + 0.3*angle[1]) + random.uniform(-0.1, 0.1)
            # z coordinate
            self.feedback[Feedback.CUBE][self.current[State.CUBE_ID]][2] = float(random.uniform(1.3, 1.4))

        for i in range(self.cubes):
            self.feedback[Feedback.CUBE_DISTANCE][i] = distance(self.feedback[Feedback.CUBE][i], self.poses.cube_goal_pose)
            # update min distance (cube from goal)
            if self.feedback[Feedback.CUBE_DISTANCE][i] < self.feedback[Feedback.MIN_CUBE_DISTANCE][i]:
                self.feedback[Feedback.MIN_CUBE_DISTANCE][i] = float(self.feedback[Feedback.CUBE_DISTANCE][i])

            self.feedback[Feedback.ROBOT_CUBE_DISTANCE][i] = distance(self.current[State.POSE], self.feedback[Feedback.CUBE][i][0:2])
            # update min distance (robot from cube)
            if self.feedback[Feedback.ROBOT_CUBE_DISTANCE][i] < self.feedback[Feedback.MIN_RC_DISTANCE][i]:
                self.feedback[Feedback.MIN_RC_DISTANCE][i] = float(self.feedback[Feedback.ROBOT_CUBE_DISTANCE][i])

        self.feedback[Feedback.ROBOT_DISTANCE] = distance(self.current[State.POSE], self.poses.place_table)

    ##############################################
    #               LOCALIZATION                 #
    ##############################################

    def localise_robot(self):
        """ Transition that allows to localize the robot """

        p_success = random.random()
        if self.sm_par.deterministic:
            p_success = 1.0

        if p_success < self.sm_par.fail_localization_probability:
            # the AMCL has an error value in the order of a couple of meters around the last known position
            self.current[State.LOCALISED] = False
            self.feedback[Feedback.FAILURE_PB] += self.sm_par.fail_localization_probability
            if self.sm_par.verbose:
                print("ERROR: localisation filter did not converge!")
        else:
            if self.sm_par.verbose:
                print("Robot Localised")
            self.current[State.LOCALISED] = True

        self.update_feedback()
        #print("LOC +7s")
        self.feedback[Feedback.ELAPSED_TIME] += 7.0
        return self.current[State.LOCALISED]

    ##############################################
    #                NAVIGATION                  #
    ##############################################

    def pose_half_way(self, pose, past_pose):
        return [(pose[0] + past_pose[0])/2, (pose[1] + past_pose[1])/2]

    def ready_to_move(self):
        """ State wheter the robot is ready to move """
        return (self.current[State.LOCALISED:State.POSE] == [True, "Up", "Tucked"]) or \
               (self.current[State.LOCALISED:State.POSE] == [True, "Up", "Pick"])

    def move_to(self, pose, safe=False):
        """ Transition that allows to move the robot to a specific pose """

        success = False
        past_pose = list(self.feedback[Feedback.AMCL])
        p_success = random.random()
        if self.sm_par.deterministic or safe:
            p_success = 1.0

        if not self.current[State.HAS_CUBE]:
            drop = 0.0
        else:
            drop = float(self.sm_par.drop_probability)

        if self.current[State.POSE] == pose:
            # the robot doesn't move
            success = True
            if self.sm_par.verbose:
                print("Robot already at requested pose.")
        elif self.ready_to_move():
            if p_success < (drop*self.sm_par.lost_probability):
                # CASE1: localisation lost during motion and cube dropped
                # the robot loses localization halfway, so let's put that on the current and feedback
                # then the update function will let the error grow
                self.current[State.POSE] = list(self.pose_half_way(pose, past_pose))
                self.feedback[Feedback.AMCL] = list(map(lambda x,y:x+y, self.current[State.POSE], [random.random()*0.1, random.random()*0.1]))
                self.current[State.LOCALISED] = False
                self.current[State.HAS_CUBE] = False
                self.feedback[Feedback.CUBE][self.current[State.CUBE_ID]] = list(self.poses.cubes_spawn_pose[self.current[State.CUBE_ID]])
                self.current[State.CUBE_ID] = None
                self.feedback[Feedback.FAILURE_PB] += drop*self.sm_par.lost_probability
                if self.sm_par.verbose:
                    print("ERROR: cube dropped AND localisation lost!")
            elif p_success - (drop*self.sm_par.lost_probability) <\
                 (1.0 - self.sm_par.lost_probability)*drop :
                # CASE2: cube dropped but localization ok
                self.current[State.POSE] = list(self.pose_half_way(pose, past_pose))
                self.current[State.HAS_CUBE] = False
                self.feedback[Feedback.CUBE][self.current[State.CUBE_ID]] = list(self.poses.cubes_spawn_pose[self.current[State.CUBE_ID]])
                self.current[State.CUBE_ID] = None
                self.feedback[Feedback.FAILURE_PB] += (1.0 - self.sm_par.lost_probability)*drop
                if self.sm_par.verbose:
                    print("ERROR: cube lost during motion!")
            elif p_success - drop <\
                 self.sm_par.lost_probability*(1.0 - drop) :
                # CASE3: localization lost
                self.current[State.POSE] = list(self.pose_half_way(pose, past_pose))
                self.feedback[Feedback.AMCL] = list(map(lambda x,y:x+y, self.current[State.POSE], [random.random()*0.1, random.random()*0.1]))
                self.current[State.LOCALISED] = False
                self.feedback[Feedback.FAILURE_PB] += self.sm_par.lost_probability*(1.0 - drop)
                if self.sm_par.verbose:
                    print("ERROR: localisation lost during motion!")
            else:
                # CASE4: all good!
                success = True
                self.current[State.POSE] = pose
                self.feedback[Feedback.AMCL] = list(map(lambda x,y:x+y, self.current[State.POSE], [random.random()*0.1, random.random()*0.1]))
                if self.sm_par.verbose:
                    print("Robot at pose " + str(pose))
        else:
            if self.sm_par.verbose:
                print("Robot not ready to move.")

        # if safe, take a 15m longer path, but there is no failure probability
        navigated_dist = distance(self.current[State.POSE], past_pose) + 15.0*int(safe)
        self.feedback[Feedback.ELAPSED_TIME] += navigated_dist/self.velocity
        #print("MOVE +" + str(navigated_dist/self.velocity) + "s")

        self.update_feedback()
        return success

    ##############################################
    #               MANIPULATION                 #
    ##############################################

    def move_arm(self, configuration):
        """ Handle the tucking of the robot arm """

        success = True
        self.current[State.ARM] = configuration
        if self.sm_par.verbose:
            print("Robot arm in {} configuration".format(configuration))

        #print("TUCK +3s")
        self.feedback[Feedback.ELAPSED_TIME] += 3.0
        if self.current[State.HAS_CUBE]:
            if self.sm_par.verbose:
                print("Cube lost, respawning at pick table.")
            self.feedback[Feedback.CUBE][int(self.current[State.CUBE_ID])] = self.poses.cubes_spawn_pose[int(self.current[State.CUBE_ID])]
            self.current[State.HAS_CUBE] = False
            self.current[State.CUBE_ID] = None

        self.update_feedback()
        return success

    def ready_to_pick(self):
        """ State wheter the robot is ready to pick """
        return self.current[State.LOCALISED:State.HAS_CUBE] == [True, "Down", "Tucked", self.poses.pick_table0] or\
               self.current[State.LOCALISED:State.HAS_CUBE] == [True, "Down", "Tucked", self.poses.pick_table1] or\
               self.current[State.LOCALISED:State.HAS_CUBE] == [True, "Down", "Tucked", self.poses.pick_table2] or\
               self.current[State.LOCALISED:State.HAS_CUBE] == [True, "Down", "Tucked", self.poses.place_table]

    def pick(self):
        """ Pick the cube """

        success = False
        p_success = random.random()
        if self.sm_par.deterministic:
            p_success = 1.0

        if self.ready_to_pick() and min(self.feedback[Feedback.ROBOT_CUBE_DISTANCE]) < 0.8:
            # this means that there is a cube to pick near to the robot
            if p_success < self.sm_par.fail_pick_probability:
                self.current[State.HAS_CUBE] = False
                self.feedback[Feedback.FAILURE_PB] += self.sm_par.fail_pick_probability
                #self.feedback[Feedback.CUBE] = list(self.poses.cube_spawn_pose)
                if self.sm_par.verbose:
                    print("ERROR: picking failed!")
            else:
                success = True
                self.current[State.HAS_CUBE] = True
                # the cube to be picked is then the closest to the robot
                self.current[State.CUBE_ID] = self.feedback[Feedback.ROBOT_CUBE_DISTANCE].index(min(self.feedback[Feedback.ROBOT_CUBE_DISTANCE]))
                self.current[State.ARM] = "Pick"
                if self.sm_par.verbose:
                    print("Cube picked.")
        else:
            if self.sm_par.verbose:
                print("Robot not ready to pick.")

        self.update_feedback()
        #print("PICK +12s")
        self.feedback[Feedback.ELAPSED_TIME] += 12.0
        return success

    def ready_to_place(self):
        """ State wheter the robot is ready to place """
        return self.current[State.LOCALISED:State.HAS_CUBE] == [True, "Down", "Tucked", self.poses.pick_table0] or\
               self.current[State.LOCALISED:State.HAS_CUBE] == [True, "Down", "Tucked", self.poses.pick_table1] or\
               self.current[State.LOCALISED:State.HAS_CUBE] == [True, "Down", "Tucked", self.poses.pick_table2] or\
               self.current[State.LOCALISED:State.HAS_CUBE] == [True, "Down", "Pick", self.poses.place_table]

    def place(self):
        """ Place the cube """

        success = False
        p_success = random.random()
        if self.sm_par.deterministic:
            p_success = 1.0

        if self.ready_to_place() and self.current[State.HAS_CUBE]:
            if p_success < self.sm_par.fail_place_probability:
                self.feedback[Feedback.FAILURE_PB] += self.sm_par.fail_place_probability
                #self.current[State.ARM] = "Place"
                #self.feedback[Feedback.CUBE] = list(self.poses.cube_spawn_pose)
                if self.sm_par.verbose:
                    print("ERROR: placing failed!")
            else:
                success = True
                self.current[State.HAS_CUBE] = False
                self.current[State.ARM] = "Place"
                if self.current[State.POSE] == self.poses.pick_table0 or\
                    self.current[State.POSE] == self.poses.pick_table1 or\
                    self.current[State.POSE] == self.poses.pick_table2:
                    self.feedback[Feedback.CUBE][self.current[State.CUBE_ID]] = list(self.poses.cubes_spawn_pose[self.current[State.CUBE_ID]])
                    if self.sm_par.verbose:
                        print("Cube placed in the pick table.")
                elif self.current[State.POSE] == self.poses.place_table:
                    self.feedback[Feedback.CUBE][self.current[State.CUBE_ID]] = list(self.poses.cube_goal_pose)
                    if self.sm_par.verbose:
                        print("Cube placed in the place table.")
                self.current[State.CUBE_ID] = None
        else:
            if self.sm_par.verbose:
                print("Robot not ready to place.")

        self.update_feedback()
        #print("PLACE +5s")
        self.feedback[Feedback.ELAPSED_TIME] += 5.0
        return success

    ##############################################
    #                   HEAD                     #
    ##############################################

    def move_head_up(self):
        """ Move the head in Up configuration """
        self.current[State.HEAD] = "Up"
        #print("UP +2s")
        self.feedback[Feedback.ELAPSED_TIME] += 2.0
        if self.sm_par.verbose:
            print("Robot head UP")
        return True

    def move_head_down(self):
        """ Move the head in Down configuration """
        self.current[State.HEAD] = "Down"
        #print("DOWN +2s")
        self.feedback[Feedback.ELAPSED_TIME] += 2.0
        if self.sm_par.verbose:
            print("Robot head DOWN")
        return True


def distance(pose1, pose2):
    """ Function implementing the distance """
    argument = 0
    for i in range(len(pose1)):
        argument += (pose1[i]-pose2[i])**2

    return math.sqrt(argument)
