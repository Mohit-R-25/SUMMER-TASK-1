from setuptools import find_packages, setup
import os
from glob import glob
package_name = 'turtle_patrol'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'),
        glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mohit',
    maintainer_email='mohit.25082006@gmail.com',
    description='Collision avoidance for turtlebot',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'collision_avoidance_node = turtle_patrol.collision_avoidance_node:main',
            'circle_patrol_server = turtle_patrol.circle_patrol_server:main',
            'circle_patrol_client = turtle_patrol.circle_patrol_client:main',
        ],
    },
)
