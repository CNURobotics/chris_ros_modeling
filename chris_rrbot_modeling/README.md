## CHRIS RRBot Demo

### Description

This example provides a demonstration of the [JointTrajectoryAction] interface
to the RRBot from [Gazebo ROS Demos]

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

 Unlike `rqt_graph`, the chris_ros_modeling tools explicitly separates action topics from regular topics.

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

This loads a simple RRBot gazebo simulation driven by the [JointTrajectoryAction] controller script `rrbot_action_demo`.

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

Snippets of code and inspiration were derived from
[Gazebo ROS Demos](https://github.com/ros-simulation/gazebo_ros_demos).
[JointTrajectoryAction](http://wiki.ros.org/joint_trajectory_action)
