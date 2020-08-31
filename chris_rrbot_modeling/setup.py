from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# fetch values from package.xml
setup_args = generate_distutils_setup(
    packages=['chris_rrbot_modeling'],
    scripts=['bin/rrbot_action_demo'],
    package_dir={'': 'src'},
    requires=['chris_rrbot_modeling']
)

setup(**setup_args)
