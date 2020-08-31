### CHRIS ROS Modeling

### Description

This Python ROS Modeling Prototype was written to provide metamodel classes and tools for
marshalling/unmarshalling instances of ROS Entity Metamodels.

In addition to the metamodels, this package includes a `model_loader` tool that
reads input from either a `YAML`- or Pickle file, and outputs to various formats.
 * Human readable "pretty" text
 * YAML format
 * Pickle format
 * DOT graph format (computation graph with nodes and topics only)

The `model_loader` tool serves as an example of how the model information from
sources, (e.g. `chris_ros_snapshot`) can be read in and used.
It is expected that this will be extended to allow exchange the model information
to other modeling formats.

### Usage

To run the `model_loader` tool, you will need to perform the following steps in addition to the Initial Setup in
the main [README](../README.md), then:
- To run this project, use this command: `rosrun chris_ros_modeling model_loader`
- The `model_loader` program assumes that an input model in either YAML or Pickle is available
  - Default input presumes YAML in `./output/yaml`
- The following command line options are available:
    - `-h`, `--help`
        - show this help message and exit
    - `-v`, `--version`
        - Display modeling version information and exit
    - `-i INPUT`, `--input=INPUT`
        - source input folder
        - (default=`output/yaml`)
    - `-t TARGET`, `--target=TARGET`
        - target output directory (default=`model_output`)
    - `-b BASE`, `--base=BASE`
        - output base file name
        - (default=`ros_model`)
    - `-a`, `--all`
        - output all possible formats
    - `-r HUMAN`, `--human=HUMAN`
        - output human readable text format to directory
        - (default=`None`)
    - `-y YAML`, `--yaml=YAML`
        - output yaml format to directory
        - (default=`None`)
    - `-p PICKLE`, `--pickle=PICKLE`
        - output pickle format to directory
        - (default=`None`)
    - `-g GRAPH`, `--graph=GRAPH`
        - output DOT format for computation graph to directory
        - (default=`None`)
    - `-d`, `--display`
        - display computation graph pdf
        - (default=`False`)
        - (only valid if graph output is specified)
    - `-s`, `--spec-only`
        - load only the ROS workspace specifications

### Known issues

This project is an ongoing development effort and may be subject to future changes.
Be warned that:
 * incomplete and/or experimental implementations are present
 * potentially incomplete error handling and/or logging
 * ongoing documentation efforts
 * some overly long names or deeply nested conditionals that may warrant refactoring

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
