from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# fetch values from package.xml
setup_args = generate_distutils_setup(
    packages=['chris_ros_snapshot'],
    scripts=['bin/ros_snapshot'],
    package_dir={'': 'src'},
    requires=['chris_ros_modeling', 'rosgraph']
)

setup(**setup_args)
