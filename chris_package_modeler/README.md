### CHRIS ROS Package Modeler

### Description

This Python tool crawls an existing ROS Workspace and generates models for all
available packages include node, message, action, and service specifications.

The output models are useful for system documentation and validation, and
for future use in model-based engineering.

These componenet metamodels are then used to create models of ROS deployments.

### Usage

The `package_modeler`  assumes that it is running on the same ROS network as a
currently deployed ROS system.

To run `package_modeler` tool, you will need to perform the following steps in addition to the Initial Setup in
the main [README](../README.md), then use this command: `rosrun chris_package_modeler package_modeler`

The default command generates an output model in both YAML and Pickle formats in the `./output` directory.
- The following command line options are available:
    - `-h`, `--help`
        - show this help message and exit
    - `-v`, `--version`
        - Display version information for the package modeler tool and exit
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
    - `-a`, `--all`
        - output all possible formats

### Output

After running `package_modeler`, the following output structure will be available:
- The main `output` directory (or as specfied by command line arguments)
  - By default, the output is located in the directory where `package_modeler` was run
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
    - `graph`: the ROS Graph DOT Output of ROS Computation graph with grouped actions


### Known issues

This project is an ongoing development effort and may be subject to future changes.
Be warned that:
 * incomplete and/or experimental implementations are present
 * potentially incomplete error handling and/or logging
 * ongoing documentation efforts
 * some overly long names or deeply nested conditionals that may warrant refactoring

 The following specific shortcomings are noted:  
  * The package modeler does NOT do static code analysis
    * We expect to add a HAROS interface in near term to supplement the basic scan
  * The package modeler identifies all executable files as potential nodes
    * Nodes are initially identified with validated=False
    * Either static analysis (e.g. HAROS) or ros_snapshot will validate some node definitions
  * The package modeler does not YET identify nodelet definitions
    * Future work will scan package files to identify plugin definitions
    * HAROS interface should provide this information
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
