### CHRIS ROS Snapshot

### Description

This Python ROS Snapshot Prototype was written to use the `roscore`-centered design of ROS 1 in order
to collect, sort, and write out detailed modeling information about Nodes (including Nodelets, Nodelet
Managers, Action Servers, and Action Clients), Topics, Messages, Services, and Actions that are registered
with a running `roscore` during runtime.

The program is also able to create and write out a directed DOT graph that details the Nodes and Topics
(including display of which Topics are used for Actions) that are registered with a running `roscore` during
runtime.  

All of this information helps to describe the
[ROS Computation Graph](http://wiki.ros.org/ROS/Concepts#ROS_Computation_Graph_Level).
Unlike, the basic `rosgraph` tool, the model-based tool provides grouped information for actions.

The output models are useful for system documentation and validation, and
for future use in model-based engineering.

### Usage

The `ros_snapshot` tool optionally works with a modified version of `roscore`, see below for more
information about that usage.

- The `ros_snapshot` program assumes that it is running on the same ROS network as a
currently deployed ROS system.

To run `ros_snapshot` tool, you will need to perform the following steps in addition to the Initial Setup in
the main [README](../README.md), then use this command: `rosrun chris_ros_snapshot ros_snapshot`

The default command generates an output model in both YAML and Pickle formats in the `./output` directory.
- The following command line options are available:
    - `-h`, `--help`
        - show this help message and exit
    - `-v`, `--version`
        - Display version information for the snapshot tool and exit
    - `-t TARGET`, `--target=TARGET`
        - target output directory (default=`output`)
    - `-b BASE`, `--base=BASE`
        - output base file name
        - (default=`ros_model`)
    - `-y YAML`, `--yaml=YAML`
        - output yaml format to directory
        - (default=`yaml`)
    - `-p PICKLE`, `--pickle=PICKLE`
        - output pickle format to directory
        - (default=`pickle`)
    - `-r HUMAN`, `--human=HUMAN`
        - output human readable text format to directory
        - (default=`None`)
    - `-g GRAPH`, `--graph=GRAPH`
        - output dot format for computation graph to directory
        - (default=`None`)
    - `-a`, `--all`
        - output all possible formats
    - `-d`, `--display`
        - display computation graph pdf
        - (default=`False`)
        - (only valid if graph output is specified)
    - `-s=SPEC`, `--spec-input=SPEC`
        - input directory holding specification modesl (default=`output/yaml`)

The custom `roscore` allows for more detailed information about parameters as they are
set and read by specific nodes.  Without the custom `roscore`, this node specific
parameter information will be missing, but the other information is the same.

To use the custom `roscore`, just clone and build the custom `ros_comm` package in your local Catkin workspace
    - `cd <catkin_ws_location>`  (e.g. the `src` folder for custom projects)
      - normally a simple `roscd` without arguments will take you there
    - `git clone https://gitlab.pcs.cnu.edu/CHRISLab/ros_comm.git`
    - `cd ros_comm`
    - `git checkout feature/add_ros_probe_alpha`
    - `catkin build` (or similar catkin build command)
    - You may want to run the `roscore` manually from this package when running future projects
        - `rosrun roslaunch roscore`
        - This step is not required as the modified `roscore` will be run for now on
        - The parameter to node mappings for the `ros_snapshot` are obtained using this modified `roscore`
    - Start your ROS system as normal
    - Then run this `ros_snapshot` tool as described above

### Output

After running `ros_snapshot`, the following output structure will be available:
- The main `output` directory (or as specfied by command line arguments)
  - By default, the output is located in the directory where `ros_snapshot` was run
- Inside the `output` directory, you will find the following sub-directories if specified:
    - `yaml`: YAML, detailed model of the deployed ROS system as instances of the metamodels in the
           sibling project: `chris_ros_modeling`)
        - This format can be loaded by the `model_loader` in `chris_ros_modeling`
    - `pickle`: A standard Python Pickle file
        - This format can be loaded by the `model_loader` in `chris_ros_modeling`
        - NOTE: Pickle files can be broken by subsequent version changes to Python or metamodels
    - `human`: human-readable, formatted version of the ROS system model
        - based on instances of the metamodels in the sibling project: `chris_ros_modeling`
        - NOTE: These files are NOT loadable; always save a YAML or Pickle version for future use
    - `dot_graph`: the ROS Graph DOT Output of ROS Computation graph with grouped actions


### Known issues

 This project is an ongoing development effort and may be subject to future changes.
 Be warned that:
  * incomplete and/or experimental implementations are present
  * potentially incomplete error handling and/or logging
  * ongoing documentation efforts
  * some overly long names or deeply nested conditionals that may warrant refactoring

The following specific shortcomings are noted:  
  * Node executable information depends on active process, so `spawner` style nodes will not have information
    * Would require changes to `roscore`, `rosrun`, or `roslaunch`
  * Does not currently handle parameter subscriptions
  * Nodelet and nodelet managers
    * Currently topic publishers/subscribers are assigned to nodelet manager not nodelets
    * Nodelets do not have the proper source code identified; only the base nodelet plugin handler
      * Likely require custom `roscore`, `rosrun`, `roslaunch`, or `plugin` handler or static analysis
    * Do not currently match nodelet or nodelet manager to node spec data
    * Left @todo on the snapshot node validation section
  * Package names are not specifically known by `roscore`, only executable location
    * See https://answers.ros.org/question/358731/retrieve-package-and-binaryscript-of-running-ros-node/
    * We currently attempt to match using node type to specification data during validation
  * We do not currently check to see if a message, action, or service specification name occurs in multiple packages
    * This will likely require static code analysis to determine, but not a likely issue
  * Python scripts may be loaded and subscribe/publish, but executable shows as loader (e.g. /usr/bin/python2) not script
    * One attempt looks at command line arguments for launched scripts
    * This causes issues with nodelets, controller manager, and other system (e.g. FlexBE)
    * May require static launch file analysis (e.g. HAROS) or other customizations
  * Folder containing specifications should only have one base filename (default `ros_model_`)
  * This has been tested under ROS Kinetic (Ubuntu 16.04) and ROS Melodic (Ubuntu 18.04)

### License Information

Released under BSD license

Copyright (c) 2020
Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
Christopher Newport University

All rights reserved.

See LICENSE with each package for more information

### Credit

- William R. Drumheller <[william.drumheller.16@cnu.edu](mailto:william.drumheller.16@cnu.edu)>
- David C. Conner <[robotics@cnu.edu](mailto:robotics@cnu.edu)>

Snippets of code and inspiration were derived from various
[ROS Comm tools](https://github.com/ros/ros_comm/tree/noetic-devel/tools).
