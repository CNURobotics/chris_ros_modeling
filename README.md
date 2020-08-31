### ROS Model-based Engineering Tools

### Description

Within this repository are Python-based [ROS](http://www.ros.org) modeling tools that
can be used to capture of software model of a ROS Workspace and running ROS deployment.

The captured model can be loaded, manipulated, and exported for documentation or use
in so called Model Integrated Computing (MIC) or Model Driven Engineering (MDE).

This repository includes the following packages:
* `chris_ros_modeling`    - ROS Entity metamodel classes and tools for marshalling/unmarshalling instances
                         of these metamodels (model)
* `chris_package_modeler` - tool to capture specification model of existing ROS workspace
* `chris_ros_snapshot`    - tools to capture models from currently running ROS deployments
* `chris_rrbot_modeling`  - a demo model based on the [RRBot](https://github.com/ros-simulation/gazebo_ros_demos)

### Initial Setup

Currently these modules require Python 2.7+, so please make sure it is installed.
> Note: The projects are currently incompatible with Python 3 due to the nature of the ROS-based dependencies.
>  Future work will upgrade to Python 3

The Python executables require `apt`, `PyYAML`, and `graphviz` packages. Use
<pre>
pip install -r requirements.txt
</pre>
> NOTE: Currently `apt` should be installed via `sudo apt install python-apt`


Once this project has been cloned into your [Catkin](https://docs.ros.org/api/catkin/html) Workspace, run the
following commands:
- `catkin build` (or similar catkin build command)
- `source <catkin_ws_location>/setup.bash` (your `.bashrc` may handle this automatically on shell restart)

From here, the packages should be available for use with `rosrun` (see the project specific `README`s for more
detail).

### Known issues

This project is an ongoing development effort and may be subject to future changes.

See the individual project READMEs for specific information.

On going work intends to incorporate HAROS static code analysis and enable export
of these models to other MIC/MDE tools.

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
