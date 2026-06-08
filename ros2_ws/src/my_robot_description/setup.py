from setuptools import find_packages, setup

package_name = 'my_robot_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
data_files=[
    (
        'share/' + package_name + '/launch',
        ['launch/display.launch.py',
         'launch/gazebo.launch.py']
    ),
    (
        'share/' + package_name + '/urdf',
        ['urdf/simple_robot.urdf.xacro']
    ),
    (
        'share/' + package_name + '/worlds',
        ['worlds/my_world.sdf']
    ),
],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mohit',
    maintainer_email='mohit.25082006@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
