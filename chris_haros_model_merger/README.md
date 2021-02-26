### CHRIS HAROS Model Merger

### Description

The CHRIS HAROS Model Merger is a model merging tool prototype for
experimentation with creating unified models (of ROS deployments)
from those generated with the chris\_ros\_modeling metamodeling
tools and from those generated with
[HAROS](https://github.com/git-afsantos/haros).
Thus, the tool attempts to create unified and comprehensive models
from both the dyanmic CHRIS ROS Snapshot Tool and the static HAROS tool.

The tool attempts to gather as much information as feasibly possible
from the model database file created by running HAROS, which includes
these types of models (some of which are extremely limited):
- Nodes
- Topics
- Services
- Parameters
- Node Specifications
- Service Specifications
- Package Specifications

*Note: The Metamodel Specification that Helps to Describe these HAROS
Models, which was the Ultimate Reference for the Development of this
Prototype can be Found
[Here in the HAROS GitHub repository](https://github.com/git-afsantos/haros/blob/master/haros/metamodel.py)*.

From there, the available data is either merged into an existing CHRIS
model, used to Validate / Update CHRIS model data, or in more challenging
cases of comparison discrepancies, displayed to the user as a warning.
If a model is not already present in a CHRIS model bank, then a basic model
is created and populated based on HAROS data and then added to the CHRIS
model bank.
Finally, the merged data is written back out to the desired model format,
which could be used for a graphical diff (if the original model data was
stored in a separate location).
Detailed logs attempt to keep the user informed of all major validation /
comparison issues and model updates.


### Requirements & Usage

The `chris_haros_model_merger` tool first requires both the
[`ros_snapshot`](../chris_ros_snapshot) tool and
[HAROS](https://github.com/git-afsantos/haros) to generate the models
necessary to create a unified, merged model.
The instructions to run each are provided in the links just provided,
but an example, which demonstrates the neccesary steps to create a merged
model, is provided [here](../chris_rrbot_modeling).

Instructions that may aid in installing HAROS based on experimentation
as well as links to the official setup instructions for HAROS are provided
[here](doc/haros_install_investigation.md).
*Note: This tool has been tested with model database output from HAROS version
`3.9.0`.*

- The following command line options are available:
    - `-h`, `--help`
        - show this help message and exit
    - `-v`, `--version`
        - display version information for the snapshot tool and exit
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
    - `-cm`, `--chris_model_input`
        - CHRIS ROS model input folder
        - (default=`output/yaml`)
    - `-hm`, `--haros_model_input`
        - HAROS ROS model input folder
        - This is also thought of as the HAROS top-level output directory
        - That directory must contain the database file `projects/default/haros.db`
        - (default=`haros_output`)
    - `-lt`, `--logger_threshold`
        - logger threshold
        - choices include `ERROR`, `WARNING`, `INFO`, and `DEBUG`
        - (default=`INFO`)


### Output

Just like after running [`ros_snapshot`](../chris_ros_snapshot), the following output
structure will once again be available:
- The main `output` directory (or as specfied by command line arguments)
  - By default, the output is located in the directory where `chris_haros_model_merger` was run
- Inside the `output` directory, you will find the following sub-directories, as specified:
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
    - The default command generates an output model in both YAML and Pickle formats in the
      `./output` directory.
*Note: The output files will contain the newly updated / merged models.*


### Known issues

This project is an ongoing development effort and may be subject to future changes.
Be warned that:
  * incomplete and/or experimental implementations are present
  * potentially incomplete error handling and/or logging
  * ongoing documentation efforts
  * some overly long names or deeply nested conditionals that may warrant refactoring

It is also worth noting that both HAROS and the CHRIS HAROS Model Merger are still
in a research and development phase.
Thus:
  * the HAROS metamodel may change at any point, causing this program to have to adapt
  * the current amount of data extracted may increase over time as HAROS expands:
    * ROS Actions are not able to be obtained
    * Nodelet Managers, if newly created and added to the CHRIS data, are not separated
      out into the Nodelet Manager Bank since HAROS does not allow for this tool to
      easily identify Nodelet Managers
    * Service Specification data is extremely limited; just the name is available
    * Many other pieces of data such as file locations may be missing since the HAROS
      metamodel did not offer a feasibly simple way of obtaining the data
    * Notes are provided within the code to show specific decisions that were made in
      these cases
  * for our purposes, it is best that these project files only focus on one HAROS
    `configuration` (see the HAROS `README` for insight into what a project
    configuration is)


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

