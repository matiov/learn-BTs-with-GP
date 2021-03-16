#!/usr/bin/env python3
"""
Implementing various py trees behaviors
"""
import os
import sys

import py_trees as pt
import state_machine as sm

def get_node_from_string(string, state_machine_):
    """
    Returns a py trees behavior or composite given the string
    """
    has_children = False

    if string == "block_goal?":
        node = BlockOnTable(state_machine_)

    elif string == "tucked?":
        node = IsTucked(state_machine_)

    elif string == "stretch":
        node = MoveArm(state_machine_, "Stretched")

    elif string == "all_up":
        node = MoveArm(state_machine_, "Up")

    elif string == "all_down":
        node = MoveArm(state_machine_, "Down")

    elif string == "tuck":
        node = MoveArm(state_machine_, "Tucked")

    elif string == "up":
        node = MoveHead_Up(state_machine_)

    elif string == "down":
        node = MoveHead_Down(state_machine_)

    elif string == "localised?":
        node = IsLocalised(state_machine_)

    elif string == "localise":
        node = Localise(state_machine_)

    elif string == "table0_visited?":
        node =  Visited(state_machine_, "pick_table0")

    elif string == "table1_visited?":
        node =  Visited(state_machine_, "pick_table1")

    elif string == "table2_visited?":
        node =  Visited(state_machine_, "pick_table2")

    elif string == "move_pick0":
        node = MoveToPose(state_machine_, "pick_table0")

    elif string == "move_pick1":
        node = MoveToPose(state_machine_, "pick_table1")

    elif string == "move_pick2":
        node = MoveToPose(state_machine_, "pick_table2")

    elif string == "move_pick_s":
        node = MoveToPose_safe(state_machine_, "pick_table0")

    elif string == "not_have_block?":
        node = NotHaveBlock(state_machine_)

    elif string == "have_block?":
        node = HaveBlock(state_machine_)

    elif string == "pick":
        node = PickUp(state_machine_)

    elif string == "move_place":
        node = MoveToPose(state_machine_, "place_table")

    elif string == "move_place_s":
        node = MoveToPose_safe(state_machine_, "place_table")

    elif string == "cube0_placed?":
        node = Placed(state_machine_, 0)

    elif string == "cube1_placed?":
        node = Placed(state_machine_, 1)

    elif string == "cube2_placed?":
        node = Placed(state_machine_, 2)

    elif string == "task_done?":
        node = Finished(state_machine_)

    elif string == "place":
        node = Place(state_machine_)

    elif string == "move_rand_1":
        node = MoveToPose(state_machine_, "random1")

    elif string == "move_rand_2":
        node = MoveToPose(state_machine_, "random2")

    elif string == "move_rand_3":
        node = MoveToPose(state_machine_, "random3")

    elif string == "move_rand_4":
        node = MoveToPose(state_machine_, "random4")

    elif string == "move_rand_5":
        node = MoveToPose(state_machine_, "random5")

    elif string == "move_rand_6":
        node = MoveToPose(state_machine_, "random6")

    elif string == "move_rand_7":
        node = MoveToPose(state_machine_, "random7")

    elif string == "move_rand_8":
        node = MoveToPose(state_machine_, "random8")

    elif string == "move_rand_9":
        node = MoveToPose(state_machine_, "random9")

    elif string == "move_spawn":
        node = MoveToPose(state_machine_, "spawn")

    elif string == "move_origin":
        node = MoveToPose(state_machine_, "origin")

    elif string == 'f(':
        node = pt.composites.Selector("Fallback")
        has_children = True

    elif string == 's(':
        node = RSequence()
        has_children = True

    else:
        raise Exception("Unexpected character", string)
    return node, has_children

class BlockOnTable(pt.behaviour.Behaviour):
    """
    Condition checking if the cube is on table
    """
    def __init__(self, state_machine_):
        self.state_machine = state_machine_
        super(BlockOnTable, self).__init__("Block on table?")

    def update(self):
        if self.state_machine.feedback[sm.Feedback.CUBE] == self.state_machine.poses.cube_goal_pose:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class IsLocalised(pt.behaviour.Behaviour):
    """
    Condition checking if the robot is localised
    """
    def __init__(self, state_machine_):
        self.state_machine = state_machine_
        super(IsLocalised, self).__init__("Localised?")

    def update(self):
        #print("Checking LOC")
        if self.state_machine.current[sm.State.LOCALISED]:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class Localise(pt.behaviour.Behaviour):
    """
    Localise behavior
    """
    def __init__(self, state_machine_):
        self.state = None
        self.state_machine = state_machine_
        super(Localise, self).__init__("Localise!")

    def initialise(self):
        if not self.state_machine.current[sm.State.LOCALISED]:
            self.state = None

    def update(self):
        #print("LOC")
        if self.state is None:
            self.state = pt.common.Status.RUNNING
        elif self.state is pt.common.Status.RUNNING:
            if self.state_machine.localise_robot():
                self.state = pt.common.Status.SUCCESS
            else:
                self.state = pt.common.Status.FAILURE
        return self.state

class MoveArm(pt.behaviour.Behaviour):
    """
    Moving arm behavior
    """
    def __init__(self, state_machine_, configuration):
        self.state = None
        self.configuration = configuration
        self.state_machine = state_machine_
        super(MoveArm, self).__init__("{} arm!".format(configuration))

    def initialise(self):
        if self.state_machine.current[sm.State.ARM] != self.configuration:
            self.state = None

    def update(self):
        if self.state is None:
            self.state = pt.common.Status.RUNNING
            self.state_machine.manipulating = True
        elif self.state is pt.common.Status.RUNNING:
            if self.state_machine.move_arm(self.configuration):
                self.state = pt.common.Status.SUCCESS
            else:
                self.state = pt.common.Status.FAILURE
            self.state_machine.manipulating = False
        return self.state

class IsTucked(pt.behaviour.Behaviour):
    """
    Condition checking if the robot arm is tucked
    """
    def __init__(self, state_machine_):
        self.state_machine = state_machine_
        super(IsTucked, self).__init__("Tucked?")

    def update(self):
        #print("Checking TUCK")
        # you don't want to tuck again if the robot has the cube
        if self.state_machine.current[sm.State.ARM] == "Tucked":
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class NotHaveBlock(pt.behaviour.Behaviour):
    """
    Condition checking if the robot does not have the cube
    """
    def __init__(self, state_machine_):
        self.state_machine = state_machine_
        super(NotHaveBlock, self).__init__("Don't have block?")

    def update(self):
        #print("Checking NOT BLOCK")
        if not self.state_machine.current[sm.State.HAS_CUBE]:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class HaveBlock(pt.behaviour.Behaviour):
    """
    Condition checking if the robot has the cube
    """
    def __init__(self, state_machine_):
        self.state_machine = state_machine_
        super(HaveBlock, self).__init__("Have block?")

    def update(self):
        #print("Checking PICK")
        if self.state_machine.current[sm.State.HAS_CUBE]:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class PickUp(pt.behaviour.Behaviour):
    """
    Picking behavior
    """
    def __init__(self, state_machine_):
        self.state = None
        self.state_machine = state_machine_
        super(PickUp, self).__init__("Pick up!")

    def initialise(self):
        if self.state_machine.feedback[sm.State.ARM] != "Pick" and not self.state_machine.current[sm.State.HAS_CUBE]:
            self.state = None

    def update(self):
        #print("PICK")
        if self.state is None:
            self.state = pt.common.Status.RUNNING
            self.state_machine.manipulating = True
        elif self.state is pt.common.Status.RUNNING:
            self.state_machine.manipulating = False
            if self.state_machine.pick():
                self.state = pt.common.Status.SUCCESS
            else:
                self.state = pt.common.Status.FAILURE

            if self.state_machine.current[sm.State.POSE] == self.state_machine.poses.pick_table0:
                self.state_machine.current[sm.State.VISITED][0] = True
            elif self.state_machine.current[sm.State.POSE] == self.state_machine.poses.pick_table1:
                self.state_machine.current[sm.State.VISITED][1] = True
            elif self.state_machine.current[sm.State.POSE] == self.state_machine.poses.pick_table2:
                self.state_machine.current[sm.State.VISITED][2] = True

        return self.state

class Placed(pt.behaviour.Behaviour):
    """
    Condition checking if the robot has placed the cube
    """
    def __init__(self, state_machine_, cube_ID):
        self.state_machine = state_machine_
        self.cube_ID = cube_ID
        super(Placed, self).__init__("Cube {} placed?".format(cube_ID))

    def update(self):
        #print("Checking PLACED")
        if self.state_machine.feedback[sm.Feedback.CUBE][self.cube_ID] == self.state_machine.poses.cube_goal_pose and not self.state_machine.current[sm.State.HAS_CUBE]:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class Place(pt.behaviour.Behaviour):
    """
    Placing behavior
    """
    def __init__(self, state_machine_):
        self.state = None
        self.state_machine = state_machine_
        super(Place, self).__init__("Place!")

    def initialise(self):
        if self.state_machine.current[sm.State.HAS_CUBE]:
            self.state = None

    def update(self):
        #print("PLACE")
        if self.state is None:
            self.state = pt.common.Status.RUNNING
            self.state_machine.manipulating = True
        elif self.state is pt.common.Status.RUNNING:
            if self.state_machine.place():
                self.state = pt.common.Status.SUCCESS
            else:
                self.state = pt.common.Status.FAILURE
            self.state_machine.manipulating = False
        return self.state

class Visited(pt.behaviour.Behaviour):
    """
    Condition checking if robot has visited a pick table and attempted the picking
    """
    def __init__(self, state_machine_, pose):
        self.pose = pose
        self.pose_idx = None
        self.state_machine = state_machine_
        super(Visited, self).__init__("{} visited?".format(pose))

    def update(self):
        if self.pose == "pick_table0": self.pose_idx = 0
        elif self.pose == "pick_table1": self.pose_idx = 1
        elif self.pose == "pick_table2": self.pose_idx = 2

        if self.state_machine.current[sm.State.VISITED][self.pose_idx]:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

class MoveToPose(pt.behaviour.Behaviour):
    """
    Move to pose behavior
    """
    def __init__(self, state_machine_, pose):
        self.state = None
        self.pose = pose
        self.sm_pose = []
        self.state_machine = state_machine_
        super(MoveToPose, self).__init__("To pose {}!".format(pose))

    def initialise(self):
        if self.pose == "pick_table0": self.sm_pose = self.state_machine.poses.pick_table0
        elif self.pose == "pick_table1": self.sm_pose = self.state_machine.poses.pick_table1
        elif self.pose == "pick_table2": self.sm_pose = self.state_machine.poses.pick_table2
        elif self.pose == "place_table": self.sm_pose = self.state_machine.poses.place_table
        elif self.pose == "random1": self.sm_pose = self.state_machine.poses.random_pose1
        elif self.pose == "random2": self.sm_pose = self.state_machine.poses.random_pose2
        elif self.pose == "random3": self.sm_pose = self.state_machine.poses.random_pose3
        elif self.pose == "random4": self.sm_pose = self.state_machine.poses.random_pose4
        elif self.pose == "random5": self.sm_pose = self.state_machine.poses.random_pose5
        elif self.pose == "random6": self.sm_pose = self.state_machine.poses.random_pose6
        elif self.pose == "random7": self.sm_pose = self.state_machine.poses.random_pose7
        elif self.pose == "random8": self.sm_pose = self.state_machine.poses.random_pose8
        elif self.pose == "random9": self.sm_pose = self.state_machine.poses.random_pose9
        elif self.pose == "origin": self.sm_pose = self.state_machine.poses.origin
        elif self.pose == "spawn": self.sm_pose = self.state_machine.poses.spawn_pose

        if self.state_machine.current[sm.State.POSE] != self.sm_pose:
            self.state = None

    def update(self):
        #print("MPiT")
        if self.state is None:
            self.state = pt.common.Status.RUNNING
            self.state_machine.moving = True
        elif self.state is pt.common.Status.RUNNING:
            if self.state_machine.move_to(self.sm_pose):
                self.state = pt.common.Status.SUCCESS
            else:
                self.state = pt.common.Status.FAILURE
            self.state_machine.moving = False
        return self.state

class MoveToPose_safe(pt.behaviour.Behaviour):
    """
    Move to palce pose behavior taking a slower but safer path
    """
    def __init__(self, state_machine_, pose):
        self.state = None
        self.pose = pose
        self.sm_pose = []
        self.state_machine = state_machine_
        super(MoveToPose_safe, self).__init__("Safely to {}!".format(pose))

    def initialise(self):
        if self.pose == "pick_table0": self.sm_pose = self.state_machine.poses.pick_table0
        elif self.pose == "place_table": self.sm_pose = self.state_machine.poses.place_table
        if self.state_machine.current[sm.State.POSE] != self.sm_pose:
            self.state = None

    def update(self):
        #print("MPlT")
        if self.state is None:
            self.state = pt.common.Status.RUNNING
            self.state_machine.moving = True
        elif self.state is pt.common.Status.RUNNING:
            if self.state_machine.move_to(self.sm_pose, safe=True):
                self.state = pt.common.Status.SUCCESS
            else:
                self.state = pt.common.Status.FAILURE
            self.state_machine.moving = False
        return self.state

class MoveHead_Up(pt.behaviour.Behaviour):
    """
    Move the head up behavior
    """
    def __init__(self, state_machine_):
        self.state = None
        self.state_machine = state_machine_
        super(MoveHead_Up, self).__init__("Head up!")

    def initialise(self):
        if not self.state_machine.manipulating and self.state_machine.current[sm.State.HEAD] != 'Up':
            self.state = None

    def update(self):
        #print("UP")
        if self.state is None:
            self.state = pt.common.Status.RUNNING
        elif self.state is pt.common.Status.RUNNING:
            if self.state_machine.move_head_up():
                self.state = pt.common.Status.SUCCESS
            else:
                self.state = pt.common.Status.FAILURE
        return self.state

class MoveHead_Down(pt.behaviour.Behaviour):
    """
    Move the head down behavior
    """
    def __init__(self, state_machine_):
        self.state = None
        self.state_machine = state_machine_
        super(MoveHead_Down, self).__init__("Head down!")

    def initialise(self):
        if not self.state_machine.moving and self.state_machine.current[sm.State.HEAD] != 'Down':
            self.state = None

    def update(self):
        #print("DOWN")
        if self.state is None:
            self.state = pt.common.Status.RUNNING
        elif self.state is pt.common.Status.RUNNING:
            if self.state_machine.move_head_down():
                self.state = pt.common.Status.SUCCESS
            else:
                self.state = pt.common.Status.FAILURE
        return self.state

class Finished(pt.behaviour.Behaviour):
    """
    Condition checking if the task is finished
    """
    def __init__(self, state_machine_):
        self.state_machine = state_machine_
        super(Finished, self).__init__("Task_done?")

    def update(self):
        #print("Checking PLACED")
        cube_dist = sum(self.state_machine.feedback[sm.Feedback.CUBE_DISTANCE])
        if cube_dist == 0.0:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE



# Reactive sequence
class RSequence(pt.composites.Selector):
    """
    Rsequence for py_trees
    Reactive sequence overidding sequence with memory, py_trees' only available sequence.

    Author: Chrisotpher Iliffe Sprague, sprague@kth.se
    """

    def __init__(self, name='Sequence', children=None):
        super(RSequence, self).__init__(name=name, children=children)

    def tick(self):
        """
        Run the tick behaviour for this selector. Note that the status
        of the tick is always determined by its children, not
        by the user customised update function.
        Yields:
            :class:`~py_trees.behaviour.Behaviour`: a reference to itself or one of its children
        """
        self.logger.debug("%s.tick()" % self.__class__.__name__)
        # Required behaviour for *all* behaviours and composites is
        # for tick() to check if it isn't running and initialise
        if self.status != pt.common.Status.RUNNING:
            # selectors dont do anything specific on initialisation
            #   - the current child is managed by the update, never needs to be 'initialised'
            # run subclass (user) handles
            self.initialise()
        # run any work designated by a customised instance of this class
        self.update()
        previous = self.current_child
        for child in self.children:
            for node in child.tick():
                yield node
                if node is child and \
                    (node.status == pt.common.Status.RUNNING or node.status == pt.common.Status.FAILURE):
                    self.current_child = child
                    self.status = node.status
                    if previous is None or previous != self.current_child:
                        # we interrupted, invalidate everything at a lower priority
                        passed = False
                        for sibling in self.children:
                            if passed and sibling.status != pt.common.Status.INVALID:
                                sibling.stop(pt.common.Status.INVALID)
                            if sibling == self.current_child:
                                passed = True
                    yield self
                    return
        # all children succeded, set succed ourselves and current child to the last bugger who failed us
        self.status = pt.common.Status.SUCCESS
        try:
            self.current_child = self.children[-1]
        except IndexError:
            self.current_child = None
        yield self
