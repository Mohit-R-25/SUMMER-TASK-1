from setuptools import setup, find_packages
from glob import glob
import os

package_name = 'robot'

setup(
    name=package_name,
    version='0.0.0',
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
        # ──── ORIGINAL ASSETS (ID 0) ────
        (os.path.join('share', package_name, 'models/aruco_marker'), glob('models/aruco_marker/model.*')),
        (os.path.join('share', package_name, 'models/aruco_marker/materials/textures'), glob('models/aruco_marker/materials/textures/*')),
        
        # ──── NEW ASSETS (ID 1) ────
        (os.path.join('share', package_name, 'models/aruco_marker_id1'), glob('models/aruco_marker_id1/model.*')),
        (os.path.join('share', package_name, 'models/aruco_marker_id1/materials/textures'), glob('models/aruco_marker_id1/materials/textures/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mohit',
    maintainer_email='mohit.25082006@gmail.com',
    description='Robot description package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'aruco_tracker = robot.aruco_tracker:main',
        ],
    },
)