import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'cone_perception'

setup(
    name=package_name,
    version='0.0.0',
    # Automatically locate python packages/modules like 'cone_perception'
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
        (
            os.path.join('share', package_name, 'urdf'),
            glob('urdf/*')
        ),
        (
            os.path.join('share', package_name, 'rviz'),
            glob('rviz/*')
        ),
        (
            os.path.join('share', package_name, 'worlds'),
            glob('worlds/*')
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*')
        ),
    ],
    entry_points={
        'console_scripts': [
            'camera_snapshot = cone_perception.camera_snapshot:main',
            'cone_detector = cone_perception.cone_detector:main',
        ],
    },
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mohit',
    maintainer_email='mohit.25082006@gmail.com',
    description='Robot description package',
    license='Apache-2.0',
)