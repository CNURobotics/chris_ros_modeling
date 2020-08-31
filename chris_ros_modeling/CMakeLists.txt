cmake_minimum_required(VERSION 3.0.2)
project(chris_ros_modeling)

find_package(catkin REQUIRED COMPONENTS
)

catkin_python_setup()

catkin_package(
#  INCLUDE_DIRS src
#  LIBRARIES ${PROJECT_NAME}
#  CATKIN_DEPENDS rosgraph
)


###########
## Build ##
###########

#############
## Install ##
#############

## Mark executable scripts (Python etc.) for installation
## in contrast to setup.py, you can choose the destination
catkin_install_python(PROGRAMS
  bin/model_loader
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

## Mark libraries for installation
## See http://docs.ros.org/melodic/api/catkin/html/howto/format1/building_libraries.html
#install(TARGETS ${PROJECT_NAME}
#  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#  RUNTIME DESTINATION ${CATKIN_GLOBAL_BIN_DESTINATION}
#)

#############
## Testing ##
#############
