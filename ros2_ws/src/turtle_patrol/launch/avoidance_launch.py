from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim'
    )

    collision_node = Node(
        package='turtle_patrol',
        executable='collision_avoidance_node',
        name='collision_avoidance_node',

        parameters=[
            {'safety_threshold': 2.0}
        ]
    )

    return LaunchDescription([
        turtlesim_node,
        collision_node
    ])