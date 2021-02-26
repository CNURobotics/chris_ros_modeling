### HAROS Installation Investigation
#### Ubuntu 18.04 - ROS Melodic / Ubuntu 16.04 - ROS Kinetic

---

#### Disclaimer - Installation Options

Please note that there are two different methods by which to install HAROS as
you will find at the `HAROS README - GitHub` page below.
These notes reflect success when setting up HAROS from the GitHub repository
and then installing its dependencies.
Further testing and successful use has been experienced when installing HAROS
from the Python Package Index,
but this has only ever been tested in an environment where HAROS was first
setup from the GitHub repository and then its dependencies were installed
(the HAROS version used from the Python Package Index was version `3.9.0`).
Either option should have the same effect, but please be aware that these notes
only describe success with the first option; the dependency install steps
should be the same regardless of which option is chosen.


#### HAROS Initial Setup

- [README - GitHub](https://github.com/git-afsantos/haros/blob/master/README.md)
- [Model Extraction README - GitHub](https://github.com/git-afsantos/haros/blob/master/MODEL_EXTRACTION.md)


#### Ubuntu 18.04 with ROS Melodic Revisit - 04MAR2020

On a fresh install of Ubuntu 18.04 and ROS Melodic and after cloning
HAROS from the GitHub repository, I then entered these commands:

- `sudo apt-get install python-pip` (I now have `pip 9.0.1 from /usr/lib/python2.7/dist-packages (python 2.7)`)
- `cd <haros_repo_location>`
- `pip install -r requirements.txt`
- `sudo apt-get install cppcheck cccc`
- `pip install -Iv clang==3.9` (older versions, such as `3.8` are not available for the next step via `apt`)
- `sudo apt-get install libclang-3.9-dev`
- `sudo apt-get install clang-3.9` (not documented in `haros` `README`)
- `pip install python-magic` (not documented in `haros` `README`)
- `python haros-runner.py init` (**very important when cloning 1st time or pulling updates from Git...**)
- See the rest of the steps below, as they will be comparable; make sure to use the path to
  `clang-3.9` (this catkin command is required for Ubuntu 18.04 though:
  `catkin build -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -DCMAKE_CXX_COMPILER=/usr/bin/clang++-3.9 -DCMAKE_CXX_STANDARD=11`)


#### Ubuntu 16.04 with ROS Kinetic Revisit - 26FEB2020

I have found that Ubuntu 16.04 and `haros` play nicely if the following steps are
performed during the installation (note that some steps may be different than what
I may have recorded elsewhere):
- I needed a newer version of `pip` (Python 2):
  - `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
  - `sudo python get-pip.py`
  -  Add `/usr/local/bin/` to `$PATH` (see `~/.profile`)
- `pip install -r requirements.txt`
- `sudo apt-get install cppcheck cccc`
- `pip install -Iv clang==3.8` (newer versions may be fine here)
- `sudo apt-get install libclang-3.8-dev` (make sure this matches the above version)
- `sudo apt-get install clang-3.8` (not documented in `haros` `README`)
- `pip install python-magic` (not documented in `haros` `README`)
- `python haros-runner.py init` (**very important when cloning 1st time or pulling updates from Git...**)


#### Initial Configuration

This new `~/.haros/configs.yaml ` file is created after running `init`:
  ```
  %YAML 1.1
  ---
  # workspace: '/path/to/ws'
  # environment: null
  # plugin_blacklist: []
  # cpp:
  #    parser_lib: '/usr/lib/llvm-3.8/lib'
  #    std_includes: '/usr/lib/llvm-3.8/lib/clang/3.8.0/include'
  #    compile_db: '/path/to/ws/build'
  # analysis:
  #    ignore:
  #        tags: []
  #        rules: []
  #        metrics: []
  ```

I had to update the `~/.haros/configs.yaml` file for proper configuration:
  ```
  %YAML 1.1
  ---
  workspace: '/home/<user>/<user_catkin_workspace>'
  # environment: null
  # plugin_blacklist: []
  cpp:
      parser_lib: '/usr/lib/llvm-3.8/lib'
      std_includes: '/usr/lib/llvm-3.8/lib/clang/3.8.0/include'
      compile_db: '/home/<user>/<user_catkin_workspace>/build'
  # analysis:
  #    ignore:
  #        tags: []
  #        rules: []
  #        metrics: []
  ```

**For properly extracting models, we must rebuild our Catkin Packages for HAROS:**
- `cd /home/<user>/<user_catkin_workspace>/src`
- `rm -rf ../build ../devel` (THIS IS A MUST!)
- `catkin build -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -DCMAKE_CXX_COMPILER=/usr/bin/clang++-3.8`
  (it seems like this is a one time operation as a `compile_commands.json` file should be
  created inside of each little project's `build` directory)

**Run HAROS with a Project File:**
- Refer back to the HAROS `README` for more information on project files
- For our purposes, it is best that these project files only focus on one HAROS `configuration`
  (see the HAROS `README` for insight into what a project configuration is)
- We will be running `haros` from the repository like this:
  - `python haros-runner.py full -n --no-cache -p <some_project_file>.yaml --data-dir haros_output`
- Or we will be running `haros` from the Python Package Installed version like this:
  - `haros full -n --no-cache -p <some_project_file>.yaml --data-dir haros_output`
- See an example of HAROS usage in the [`chris_rrbot_modeling`](../../chris_rrbot_modeling) README
