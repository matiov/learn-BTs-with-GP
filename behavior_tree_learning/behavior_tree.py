#!/usr/bin/env python3
# pylint: disable=global-at-module-level, global-statement, global-variable-undefined
"""
Class for handling string representations of behavior trees
"""
import random
import yaml

""" Below are lists of the possible node types """
global FALLBACK_NODES
"""
A list of all types of fallback nodes used, typically just one
"""

global SEQUENCE_NODES
"""
A list of all types of sequence nodes used, typically just one
"""

global CONTROL_NODES
"""
Control nodes are nodes that may have one or more children/subtrees.
Subsequent nodes will be children/subtrees until the corresponding up character is reached
List will contain FALLBACK_NODES, SEQUENCE_NODES and any other control nodes, e.g. parallel nodes
"""

global CONDITION_NODES
"""
Condition nodes are childless leaf nodes that never return RUNNING state. They may never be the last child of any parent.
"""

global ACTION_NODES
"""
Condition nodes are also childless leaf nodes but may return RUNNING state. They may
also be the last child of any parent.
"""

global ATOMIC_FALLBACK_NODES
"""
Atomic fallback nodes are fallback nodes that have a predetermined set of children/subtrees
that cannot be changed.  They behave mostly like action nodes except that they may not be the
children of fallback nodes. Length is counted as one.
"""
global ATOMIC_SEQUENCE_NODES
"""
Atomic sequence nodes are sequence nodes that have a predetermined set of children/subtrees
that cannot be changed.  They behave mostly like action nodes except that they may not be the
children of sequence nodes. Length is counted as one.
"""

global UP_NODE
"""
The up node is not really a node but a character that marks the end of a control nodes
set of children and subtrees
"""

global LEAF_NODES
"""
CONDITIONS + ACTION_NODES + ATOMIC_FALLBACK_NODES + ATOMIC_SEQUENCE_NODES
Any kind of leaf node.
"""

global BEHAVIOR_NODES
"""
ACTION_NODES + ATOMIC_FALLBACK_NODES + ATOMIC_SEQUENCE_NODES
Basically leaf nodes that actually do something and that may be implemented as the last child.
"""

global ALL_NODES
"""
All list of all the nodes
"""

def load_settings_from_file(file):
    """
    Sets the lists of allowed nodes module wide.
    """
    global FALLBACK_NODES
    global SEQUENCE_NODES
    global CONTROL_NODES
    global CONDITION_NODES
    global ACTION_NODES
    global ATOMIC_FALLBACK_NODES
    global ATOMIC_SEQUENCE_NODES
    global UP_NODE
    global LEAF_NODES
    global BEHAVIOR_NODES
    global ALL_NODES

    FALLBACK_NODES = []
    SEQUENCE_NODES = []
    CONTROL_NODES = []
    CONDITION_NODES = []
    ACTION_NODES = []
    ATOMIC_FALLBACK_NODES = []
    ATOMIC_SEQUENCE_NODES = []
    LEAF_NODES = []
    BEHAVIOR_NODES = []
    ALL_NODES = []

    with open(file) as f:
        BT_SETTINGS = yaml.load(f, Loader=yaml.FullLoader)
    try: 
        FALLBACK_NODES = BT_SETTINGS["fallback_nodes"]
        if FALLBACK_NODES is None:
            FALLBACK_NODES = []
    except KeyError:
        pass
    try: 
        SEQUENCE_NODES = BT_SETTINGS["sequence_nodes"]
        if SEQUENCE_NODES is None:
            SEQUENCE_NODES = []
    except KeyError:
        pass
    try:
        CONTROL_NODES = BT_SETTINGS["control_nodes"]
    except KeyError:
        pass
    CONTROL_NODES += FALLBACK_NODES
    CONTROL_NODES += SEQUENCE_NODES
    ALL_NODES += CONTROL_NODES
    try:
        CONDITION_NODES = BT_SETTINGS["condition_nodes"]
    except KeyError:
        pass
    LEAF_NODES += CONDITION_NODES
    ALL_NODES += CONDITION_NODES
    try:
        ACTION_NODES = BT_SETTINGS["action_nodes"]
    except KeyError:
        pass
    BEHAVIOR_NODES += ACTION_NODES
    ALL_NODES += ACTION_NODES
    try:
        ATOMIC_FALLBACK_NODES = BT_SETTINGS["atomic_fallback_nodes"]
        if ATOMIC_FALLBACK_NODES is None:
            ATOMIC_FALLBACK_NODES = []
    except KeyError:
        pass
    BEHAVIOR_NODES += ATOMIC_FALLBACK_NODES
    ALL_NODES += ATOMIC_FALLBACK_NODES
    try:
        ATOMIC_SEQUENCE_NODES = BT_SETTINGS["atomic_sequence_nodes"]
        if ATOMIC_SEQUENCE_NODES is None:
            ATOMIC_SEQUENCE_NODES = []
    except KeyError:
        pass
    BEHAVIOR_NODES += ATOMIC_SEQUENCE_NODES
    ALL_NODES += ATOMIC_SEQUENCE_NODES
    try:
        UP_NODE = BT_SETTINGS["up_node"]
    except KeyError:
        pass
    ALL_NODES += UP_NODE
    LEAF_NODES += BEHAVIOR_NODES


def get_action_list():
    """
    Returns list of actions
    """
    global ACTION_NODES
    return ACTION_NODES

class BT:
    """
    Class for handling string representations of behavior trees
    """

    def __init__(self, bt):
        """
        Creates a bt
        """
        self.bt = bt[:]

    def set(self, bt):
        """
        Sets bt string
        """
        self.bt = bt[:]
        return self

    def random(self, length):
        """
        Creates a random bt of the given length
        Tries to follow some of the rules for valid trees to speed up the process
        """
        global CONTROL_NODES
        global ACTION_NODES
        global UP_NODE
        global BEHAVIOR_NODES

        self.bt = []
        while not self.is_valid():
            if length == 1:
                self.bt = [random.choice(BEHAVIOR_NODES)]
            else:
                self.bt = [random.choice(CONTROL_NODES)]
                for _ in range(length - 1):
                    if self.bt[-1] in CONTROL_NODES:
                        next = [self.random_node()]
                        while next in UP_NODE:
                            next = [self.random_node()]
                        self.bt += next
                    else:
                        self.bt += [self.random_node()]

                    if self.bt[-1] in ACTION_NODES:
                        self.bt += [UP_NODE[0]]

                for _ in range(length - self.length() - 1):
                    # add nodes to match the number of individuals defined in length
                    # this is required when random node gives 'up' nodes
                    # condition nodes make it more likely to be valid
                    self.bt += [random.choice(CONDITION_NODES)]
                if self.length() < length:
                    self.bt += [random.choice(BEHAVIOR_NODES)]
                self.close()

        return self.bt

    def is_valid(self):
        """
        Checks if bt is a valid behavior tree.
        Checks are somewhat in order of likelihood to fail.
        """
        global CONTROL_NODES
        global UP_NODE
        global ALL_NODES

        valid = True

        #Empty string
        if len(self.bt) <= 0:
            valid = False

        # The first element cannot be a leaf if after it there are other elements
        elif (self.bt[0] not in CONTROL_NODES) and (len(self.bt) != 1):
            valid = False

        else:
            for i in range(len(self.bt) - 1):
                #'up' directly after a control node
                if (self.bt[i] in CONTROL_NODES) and (self.bt[i+1] in UP_NODE):
                    valid = False
                #Identical condition nodes directly after one another - waste
                elif self.bt[i] in CONDITION_NODES and self.bt[i] == self.bt[i+1]:
                    valid = False
                # check for non-BT elements
                elif self.bt[i] not in ALL_NODES:
                    valid = False

            if valid:
                # Check on the bt depth: to be > 0
                depth = self.depth()
                if (depth < 0) or (depth == 0 and len(self.bt) > 1):
                    valid = False

            if valid and self.bt[0] in CONTROL_NODES:
                fallback_allowed = True
                sequence_allowed = True
                if self.bt[0] in FALLBACK_NODES:
                    fallback_allowed = False
                elif self.bt[0] in SEQUENCE_NODES:
                    sequence_allowed = False
                valid = self.is_subtree_valid(self.bt[1:], fallback_allowed, sequence_allowed)
        return valid

    def is_subtree_valid(self, string, fallback_allowed, sequence_allowed):
        """
        Checks whether the subtree starting with string[0] is valid according to a few rules
        1. Fallbacks must not be children of fallbacks
        2. Sequences must not be children of sequences
        3. Last children must not be conditions
        """
        global CONTROL_NODES
        global CONDITION_NODES
        global ACTION_NODES
        global ATOMIC_FALLBACK_NODES
        global ATOMIC_SEQUENCE_NODES
        global UP_NODE

        while len(string) > 0:
            node = string.pop(0)

            if node in UP_NODE:
                return True
            elif node in CONDITION_NODES:
                if len(string) > 0 and string[0] in UP_NODE:
                    return False
            elif node in ATOMIC_FALLBACK_NODES:
                if not fallback_allowed:
                    return False
            elif node in ATOMIC_SEQUENCE_NODES:
                if not sequence_allowed:
                    return False
            elif node in CONTROL_NODES:
                if node in FALLBACK_NODES:
                    if fallback_allowed:
                        if not self.is_subtree_valid(string, False, True):
                            return False
                    else:
                        return False
                elif node in SEQUENCE_NODES:
                    if sequence_allowed:
                        if not self.is_subtree_valid(string, True, False):
                            return False
                    else:
                        return False
                else:
                    if not self.is_subtree_valid(string, True, True):
                        return False

        return False

    def close(self):
        """
        Adds missing up nodes at the end, or removes from the end if too many
        """
        global CONTROL_NODES
        global UP_NODE
        open_subtrees = 0

        #Make sure tree always ends with up node if starts with control node
        if len(self.bt) > 0:
            if self.bt[0] in CONTROL_NODES and self.bt[len(self.bt)-1] not in UP_NODE:
                self.bt += UP_NODE

        for node in self.bt:
            if node in CONTROL_NODES:
                open_subtrees += 1
            elif node in UP_NODE:
                open_subtrees -= 1

        if open_subtrees > 0:
            for _ in range(open_subtrees):
                self.bt += UP_NODE
        elif open_subtrees < 0:
            for _ in range(-open_subtrees):
                #Do not remove the very last node, and only up nodes
                for j in range(len(self.bt) - 2, 0, -1): # pragma: no branch, we will always find an up
                    if self.bt[j] in UP_NODE:
                        self.bt.pop(j)
                        break

    def depth(self):
        """
        Returns depth of the bt
        """
        global CONTROL_NODES
        global UP_NODE
        depth = 0
        max_depth = 0

        for i in range(len(self.bt)):
            if self.bt[i] in CONTROL_NODES:
                depth += 1
                max_depth = max(depth, max_depth)
            elif self.bt[i] in UP_NODE:
                depth -= 1
                if (depth < 0) or (depth == 0 and i is not len(self.bt) - 1):
                    return -1

        if depth != 0:
            return -1

        return max_depth

    def length(self):
        """
        Counts number of nodes in bt. Doesn't count up characters.
        """
        global UP_NODE
        length = 0
        for node in self.bt:
            if node not in UP_NODE:
                length += 1
        return length

    def random_node(self):
        """
        Returns a random node.
        Usually the set of leaf nodes is much larger than the set of
        control nodes but we still typically want the final distribution to
        be approximately 50-50 between node types so this function reflects that.
        (Typically slightly more leaf nodes than control nodes, but this really depends)
        Deciding on the frequency of a random up node is more difficult.
        We now simply group them with control nodes because they are connected in some sense
        and even while there are usually more control nodes than up nodes (just one), the
        control nodes are more likely to improve the bt.
        """
        global CONTROL_NODES
        global LEAF_NODES
        global UP_NODE

        if random.random() < 0.5:
            return random.choice(CONTROL_NODES + UP_NODE)
        else:
            if random.random() < 0.3:
                return random.choice(CONDITION_NODES)
            else:
                return random.choice(ACTION_NODES)

    def change_node(self, index, new_node=None):
        """
        Changes node at index
        """
        global CONTROL_NODES
        global CONDITION_NODES
        global BEHAVIOR_NODES
        global LEAF_NODES
        global UP_NODE

        if new_node is None:
            new_node = self.random_node()

        # Change control node to leaf node, remove corresponding up
        if new_node in LEAF_NODES and self.bt[index] in CONTROL_NODES:
            self.bt.pop(self.find_up_node(index))
            self.bt[index] = new_node

        # Change leaf node to control node. Add up and extra condition/behavior node child
        elif new_node in CONTROL_NODES and self.bt[index] in LEAF_NODES:
            old_node = self.bt[index]
            self.bt[index] = new_node
            if old_node in BEHAVIOR_NODES:
                self.bt.insert(index + 1, random.choice(LEAF_NODES))
                self.bt.insert(index + 2, old_node)
            else: #CONDITION_NODE
                self.bt.insert(index + 1, old_node)
                self.bt.insert(index + 2, random.choice(BEHAVIOR_NODES))
            self.bt.insert(index + 3, UP_NODE[0])
        else:
            self.bt[index] = new_node

    def add_node(self, index, new_node=None):
        """
        Adds new node at index,
        If a control node is added in the middle,
        and it is either a sequence or a fallback node,
        we must add another of the opposite type in order
        to make sure that they are alternated and avoid
        creating an invalid tree
        """
        global CONTROL_NODES
        global LEAF_NODES
        global BEHAVIOR_NODES
        global UP_NODE

        if new_node is None:
            new_node = self.random_node()
        if new_node in CONTROL_NODES:
            if index == 0:
                #Adding new control node to encapsulate entire tree
                self.bt.insert(index, new_node)
                self.bt.append(UP_NODE[0])
            else:
                parent = self.find_parent(index)
                upper = None
                lower = None
                if new_node in FALLBACK_NODES and parent in FALLBACK_NODES:
                    upper = random.choice(SEQUENCE_NODES)
                    lower = new_node
                elif new_node in SEQUENCE_NODES and parent in SEQUENCE_NODES:
                    upper = random.choice(FALLBACK_NODES)
                    lower = new_node
                else:
                    child_control_nodes = self.find_child_control_nodes(index)
                    if new_node in FALLBACK_NODES and any(self.bt[c] in FALLBACK_NODES for c in child_control_nodes):
                        upper = new_node
                        lower= random.choice(SEQUENCE_NODES)
                    elif new_node in SEQUENCE_NODES and any(self.bt[c] in SEQUENCE_NODES for c in child_control_nodes):
                        upper = new_node
                        lower= random.choice(FALLBACK_NODES)
                if upper is not None:
                    #Requirement issues, must add two new control nodes
                    self.bt.insert(index, upper)
                    if random.random() < 0.5:
                        #Put lower control node on the right, new leaf on left
                        self.bt.insert(index + 1, random.choice(LEAF_NODES))
                        self.bt.insert(index + 2, lower)
                        up_node_index = self.find_up_node(index + 2)
                        self.bt.insert(up_node_index, UP_NODE[0])
                        self.bt.insert(up_node_index + 1, UP_NODE[0])
                    else:
                        #Put lower control node on the left, new leaf on right
                        self.bt.insert(index + 1, lower)
                        up_node_index = self.find_up_node(index + 1)
                        self.bt.insert(up_node_index, UP_NODE[0])
                        self.bt.insert(up_node_index + 1, random.choice(BEHAVIOR_NODES))
                        self.bt.insert(up_node_index + 2, UP_NODE[0])
                else:
                    #No requirement issues, can just add control node with remaining
                    #"siblings" as children.
                    self.bt.insert(index, new_node)
                    up_node_index = self.find_up_node(index)
                    if up_node_index == index + 1:
                        self.bt.insert(index + 1, random.choice(LEAF_NODES))
                        self.bt.insert(index + 2, random.choice(BEHAVIOR_NODES))
                        self.bt.insert(index + 3, UP_NODE[0])
                    else:
                        self.bt.insert(up_node_index, UP_NODE[0])

                if self.bt[index - 1] in CONTROL_NODES:
                    #New control node took all children from parent, add one new child 
                    #so parent has at least two
                    if random.random() < 0.5:
                        #To the left
                        self.bt.insert(index, random.choice(LEAF_NODES))
                    else:
                        #To the right
                        up_node_index = self.find_up_node(index)
                        self.bt.insert(up_node_index + 1, random.choice(BEHAVIOR_NODES))
        else:
            self.bt.insert(index, new_node)

    def delete_node(self, index, delete_children=True):
        """
        Deletes node at index
        """
        global CONTROL_NODES
        global LEAF_NODES
        global UP_NODE

        if self.bt[index] in LEAF_NODES:
            # if the leaf is in [..., 'control(', 'leaf', ')', ...] we remove the whole sub-tree
            while index > 0 and index + 1 < len(self.bt) and \
                    self.bt[index - 1] in CONTROL_NODES and self.bt[index+1] in UP_NODE:
                self.bt.pop(index - 1) #control node
                self.bt.pop(index) #up node
                index -= 1 #move index back to leaf node

        elif self.bt[index] in CONTROL_NODES:
            if delete_children:
                child_control_nodes = self.find_child_control_nodes(index + 1)
                if child_control_nodes != []:
                    #Not bottom, delete child control nodes to make sure that tree is valid
                    for child in reversed(child_control_nodes):
                        self.delete_node(child, delete_children=False)
            self.bt.pop(self.find_up_node(index))

        self.bt.pop(index)

    def find_parent(self, index):
        """
        Returns index of the closest parent to the node at input index
        """
        global CONTROL_NODES
        global UP_NODE

        if index == 0:
            return None
        else:
            parent = index
            siblings_left = 0
            while parent > 0:
                parent -= 1
                if self.bt[parent] in CONTROL_NODES:
                    if siblings_left == 0:
                        return parent
                    else:
                        siblings_left -= 1
                elif self.bt[parent] in UP_NODE:
                    siblings_left += 1
            return None

    def find_child_control_nodes(self, index):
        """
        Find children at the same level from
        index and forward that are fallback or sequence type
        """

        children = []
        child = index
        level = 0
        while level >= 0: 
            if level == 0 and (self.bt[child] in FALLBACK_NODES or self.bt[child] in SEQUENCE_NODES):
                    children.append(child)

            if self.bt[child] in CONTROL_NODES:
                level += 1
            elif self.bt[child] in UP_NODE:
                level -= 1
            child += 1

        return children

    def find_up_node(self, index):
        """
        Returns index of the up node connected to the control node at input index
        """
        global CONTROL_NODES
        global UP_NODE

        if self.bt[index] not in CONTROL_NODES:
            raise Exception('Invalid call. Node at index not a control node')

        if index == 0:
            if self.bt[len(self.bt)-1] in UP_NODE:
                index = len(self.bt) - 1
            else:
                raise Exception('Changing invalid BT. Missing up.')
        else:
            level = 1
            while level > 0:
                index += 1
                if index == len(self.bt):
                    raise Exception('Changing invalid BT. Missing up.')
                if self.bt[index] in CONTROL_NODES:
                    level += 1
                elif self.bt[index] in UP_NODE:
                    level -= 1

        return index

    def get_subtree(self, index):
        """
        Get subtree starting at index
        """
        subtree = []

        if self.bt[index] in LEAF_NODES:
            subtree = [self.bt[index]]
        elif self.bt[index] in CONTROL_NODES:
            subtree = self.bt[index : self.find_up_node(index) + 1]
        else:
            subtree = []

        return subtree

    def swap_subtrees(self, bt2, index1, index2):
        """
        Swaps two subtrees at given indices
        """
        subtree1 = self.get_subtree(index1)
        subtree2 = bt2.get_subtree(index2)

        if subtree1 != [] and subtree2 != []:
            # Remove subtrees
            for _ in range(len(subtree1)):
                self.bt.pop(index1)
            for _ in range(len(subtree2)):
                bt2.bt.pop(index2)

            # Insert swapped subtrees
            for i in range(len(subtree2)):
                self.bt.insert(index1 + i, subtree2.pop(0))
            for i in range(len(subtree1)):
                bt2.bt.insert(index2 + i, subtree1.pop(0))

    def is_subtree(self, index):
        """
        Checks if node at index is root of a subtree
        """
        return bool(0 <= index < len(self.bt) and self.bt[index] not in UP_NODE)
