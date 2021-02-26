## CHRIS RRBot Demo

### Description

This example provides a demonstration of the [JointTrajectoryAction](http://wiki.ros.org/joint_trajectory_action)
interface to the RRBot from [Gazebo ROS Demos](https://github.com/ros-simulation/gazebo_ros_demos).

The package includes an example model extracted using `chris_ros_modeling` tools.
These tools provide means of documenting existing ROS deployments for interface control
documents and model-based engineering.

### Modeling Tools Demonstration

To load the example model, and export to a human readable file run the following:

<pre>
roscd chris_rrbot_modeling
rosrun chris_ros_modeling model_loader -i example/yaml -t test_output --human human -y yaml -p pickle -g graph -d
</pre>

This will load the example model from `yaml` format, and write to the test_output target folder in:
 * human readable
 * yaml (also human readable, but with more clutter)
 * pickle
 * graph (dot file format)
 And display the resulting computation graph.


### Modeling Generation Demonstration with RRBot Action Demonstration

First, generate a model of your ROS system workspace specifications
<pre>
roscd chris_rrbot_modeling
rosrun chris_package_modeler package_modeler -t specifications --base rrbot_demo
</pre>
This will generate the specification models using metamodels defined in `chris_ros_modeling`, and
place the `pickle` and `yaml` formats in the `specifications` target folder.


Now run the RRBot demonstration:
<pre>
roscore
roslaunch rrbot_gazebo rrbot_world.launch
roslaunch chris_rrbot_modeling rrbot_control_action.launch
roslaunch chris_rrbot_modeling rrbot_rqt_action.launch
rosrun chris_rrbot_modeling rrbot_action_demo
</pre>

This loads a simple RRBot gazebo simulation driven by the
[JointTrajectoryAction](http://wiki.ros.org/joint_trajectory_action) controller script `rrbot_action_demo`.

While running, use `chris_ros_snapshot` to generate a model of this deployed system.
<pre>
roscd chris_rrbot_modeling
rosrun chris_ros_snapshot ros_snapshot -s specifications/pickle -t rrbot_demo -d --graph graph --base rrbot_demo --human human --yaml yaml --pickle pickle
</pre>

This loads the specification from the `pickle` format in the `specifications` folder,
generates the model of the  RRBot deployment in the `rrbot_demo` target folder,
and writes the output in `pickle`, `yaml`, `human`, `graph` and displays the computation graph.

See the `rosrun chris_ros_snapshot --help` for all options.

Compare your deployment to the provided example.


### Model Merging Demonstration with HAROS

At this point, it will be assumed that a set of CHRIS models has already been generated with `chris_ros_snapshot`
based on the instructions above.
If this is the case, then the `example/yaml` references for the pre-generated, example CHRIS models
can be replaced with the path to the newly generated set of CHRIS models.

First, an HAROS project file needs to be created based on the RRBot demonstration's launch files (please note that
only launch files can be specified in the HAROS project file).
Luckily, a pre-generated project file is available at `model_merger_example/rrbot.yaml`.

Examples were run with HAROS version `3.9.0` from the Python Package Index for convenience (but please note that
additional setup was required for model extraction, which was performed as part of an install from the GitHub HAROS
repository).
More information on HAROS installation, configuration, and usage can be found
[here](../chris_haros_model_merger/doc/haros_install_investigation.md).

Now that the project file is available, the following commands can be run:

<pre>
roscd chris_rrbot_modeling
cd model_merger_example
mkdir haros_output
haros full -n --no-cache -p rrbot.yaml --data-dir haros_output
</pre>

HAROS will open the visualizer which will allow you to validate the extracted models.
To re-do the visualization with a previously extracted model, use `haros viz -d <DATA_DIR>`,
where `DATA_DIR` is the path to output directory (e.g. `haros_output`).

After exiting the running instance of HAROS, follow the rest of these commands:

<pre>
rosrun chris_haros_model_merger model_merger -hm haros_output -cm ../example/yaml -lt ERROR
</pre>

This will run the `chris_haros_model_merger` in an attempt to merge the CHRIS models with the HAROS models to create
a more unified, comprehensive set of models for the RRBot demonstration.
The `-lt ERROR` argument allows for only `ERROR` messages to be shown; it is important
to review these messages as in some cases, these errors describe what may have
impacted the merged model (errors often just hint at validation issues and
still allow for a functional model to be created).
Output will be available at `model_merger_example/output/yaml`, which can be visually compared against the original
CHRIS models found in `example/yaml` using a visual diff program like so (alternative programs can be used):

<pre>
diff ../example/yaml/ output/yaml/

kompare ../example/yaml/ output/yaml/
</pre>

For convenience and for quick comparison, a pre-generated, example, merged model is available at
`model_merger_example/example_merged_output/yaml`.


### Known issues

  * This has been tested under ROS Kinetic (Ubuntu 16.04) and ROS Melodic (Ubuntu 18.04)
  * The RRBot performance in Melodic does not match that in Kinetic
    * Gains are adjusted for demonstration, but neither simulation or PID gains are *tuned*
  * The ROS controllers are loaded into the Gazebo controller manager, but not recognized as nodes or nodelets

### License Information

Released under BSD license

Copyright (c) 2020
Capable Humanitarian Robotics and Intelligent Systems Lab (CHRISLab)
Christopher Newport University

All rights reserved.

See LICENSE with each package for more information

### Credit

- David Conner <[robotics@cnu.edu](mailto:robotics@cnu.edu)>
- William R. Drumheller <[william.drumheller.16@cnu.edu](mailto:william.drumheller.16@cnu.edu)>
