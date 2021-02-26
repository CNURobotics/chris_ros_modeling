from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# fetch values from package.xml
setup_args = generate_distutils_setup(
    packages=['chris_haros_model_merger'],
    scripts=['bin/model_merger'],
    package_dir={'': 'src'},
    requires=['chris_ros_modeling']
)

setup(**setup_args)
