# Learning Behavior Trees with Genetic Programming in unpredictable environments

This repository contains an implementation of a Genetic Programming (GP) algorithm that evolves Behavior Trees (BTs) to solve different mobile manipulation tasks. The tasks consist in picking (from 1 to 3) cubes from tables of the environment and placing them in a different _placing_ table (see figure below). The BTs are executed in a high level state machine to make the problem computationally tractable, but they can be exported and run in a physical simulator (the code for the simulation in Gazebo with the learned BT can be provided upon request).

<p align="center">
  <img src=https://github.com/matiov/learn-BTs-with-GP/blob/master/plots/gazebo_world.png width="700" height="450">
</p>

### Notes on installation

After cloning the repository, run the following command to install the correct dpeendencies:
```bash
pip3 install -r requirements.txt
```

The Behavior Tree library is based on `py-trees==0.6.8` (see [documentation](https://py-trees.readthedocs.io/en/devel/) and [repository](https://github.com/splintered-reality/py_trees/tree/release/0.6.x)), which is the version used by `py-tree-ros` (see [repository](https://github.com/splintered-reality/py_trees_ros)) for the ROS distribution Melodic. 

In particular, the following modifications have been made to the `py_trees` source code:
* the function `pt.display.render_dot_tree` has been modified to take as input parameter the path of the target folder to save the figure;
* the function `pt.display.render_dot_tree` has been modified to display ' ' (spaces) instead of * to distinguish nodes of the same type (e.g. for two Sequence nodes, the first one has name 'Sequence' and the second one has name 'Sequence ' instead of 'Sequence*').

## Content
* `behavior_tree.py` is a class for handling string representations of behavior trees.
* `behaviors.py` contains the implementation of all behaviors used in the simulations.
* `cost_function.py` is used to compute the cost function, the costs are defined here.
* `environment.py` handles the scenarios configurations and executes the BT, returning the fitness score.
* `genetic_programming.py` implements the GP algorithm, with many possible settings.
* `gp_bt_interface.py` provides an interface between a GP algorithm and behavior tree functions.
* `py_trees_interface.py` provides an interface between `py_trees`([documentation](https://py-trees.readthedocs.io/en/devel/) and [repository](https://github.com/splintered-reality/py_trees)) and the string representation of the BTs.
* `state_machine.py` is an high-level simulator used to simulate the execution of the BTs. It is probabilistic as state transitions are regulated by the success probabilities of specific events.

* `hash_table.py` and `logplot.py` are utilities for data storage and visualization.



## Task description
There configuration files `.yaml` contain the list of behaviors used in the different tasks discussed [here](https://arxiv.org/abs/2011.03252).
In particular, the `evironment` script is configured to run configurations of type `BT_scenario_X.yaml`, so it is necessary to make the following modifications:

###### _'Effects of adding non-essential behaviors'_
Execute the first scenario in the nominal settings described in the paper.
This will create the logs for the _Necessary behaviors_.
Rename`BT_scenario_1_lowNoise.yaml` as `BT_scenario_1.yaml`.
This will create the logs for the _7 non-essential behaviors_.
Rename`BT_scenario_1_highNoise.yaml` as `BT_scenario_1.yaml`.
This will create the logs for the _14 non-essential behaviors_.

###### _'Impact of the failure probability cost on the fitness function'_
Rename`BT_scenario_1_safe.yaml` as `BT_scenario_1.yaml` and modify the following parameters for the State Machine in `state_machine.py`:
| Parameter name               | Value |
| ---------------------------- | -----:|
|fail_pick_probability         | 0.2   |                     
|fail_place_probability        | 0.1   |                   
|fail_tuck_probability         | 0.0   |                    
|fail_localization_probability | 0.2   |         
|fail_navigation_probability   | 0.0   |          
|drop_probability              | 0.2   |                      
|lost_probability              | 0.4   |

This will create the logs for the _Risky path_.
Rename`BT_scenario_1_safe.yaml` as `BT_scenario_1.yaml` and modify the value `failure: float = 0.0` to `150.0` in `cost_function.py`.
This will create the logs for the _Safe path_.

## Run the simulation
Firstly, it is necessary to create the _logs_ folder.
The `main.py` script is already configured to run the 3 scenarios described in the paper, but the script can be easily modified to run solely the first scenario, for the scope of obtaining the same results as in the paper.
The parameters for the BT execution (e.g. number of ticks, successes and failures) can be modified in `py_trees_interface.py`.

## Testing
Some BTs can be tested, to understand how they interact with the state machine simulator and to see how the fitness is computed.
To do so, run
```bash
$ pytest -s tests/test_fitness.py
```
from the repository root.

## Media
The BT solving the task in the State Machine can be shown to solve the same task designed in a physical simulator, e.g. Gazebo.
A video showing this transfer, can be found [here](https://drive.google.com/file/d/13Hyf4pMfJx3BadHIUEdJkyFBZyBQZU4i/view?usp=sharing).

###### Behavior Trees solving the first scenario
<p align="center">
  <img src=https://github.com/matiov/learn-BTs-with-GP/blob/master/plots/BT_scenario1.svg width="500" height="270">
</p>

###### Behavior Trees solving the second scenario
<p align="center">
  <img src=https://github.com/matiov/learn-BTs-with-GP/blob/master/plots/BT_scenario2.svg width="700" height="300">
</p>

###### Behavior Trees solving the third scenario
<p align="center">
  <img src=https://github.com/matiov/learn-BTs-with-GP/blob/master/plots/BT_scenario3.svg width="700" height="300">
</p>

###### Hand-coded Behavior Trees solving the third scenario
<p align="center">
  <img src=https://github.com/matiov/learn-BTs-with-GP/blob/master/plots/BT_scenario3_handcoded.svg width="900" height="270">
</p>
