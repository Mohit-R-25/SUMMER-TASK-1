import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import xacro

def generate_launch_description():

    # 1. Paths Setup
    pkg_path = get_package_share_directory('cone_perception')
    
    urdf_file = os.path.join(pkg_path, 'urdf', 'my_robot.urdf.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'my_world.sdf')
    rviz_config_path = os.path.join(pkg_path, 'rviz', 'urdf_config.rviz')

    # 2. Process Xacro to get robot_description
    robot_description_config = xacro.process_file(urdf_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    

    # 3. Nodes & Processes definitions

    # Start Ignition Gazebo
# Start Ignition Gazebo (Using official ros_gz_sim launcher with Auto-Run enabled)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description],
        output='screen'
    )

    # Spawn Robot into Gazebo (Delayed by 5 seconds)
    spawn_robot = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-topic', 'robot_description',
                    '-name', 'my_robot'
                ],
                output='screen'
            )
        ]
    )

    # RViz2 Node
    # rviz2_node = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     arguments=['-d', rviz_config_path],
    #     output='screen'
    # )

    # joint_state_publisher=Node(
    #     package='joint_state_publisher',
    #     executable='joint_state_publisher',
    #     output='screen'
    # )

    # Gazebo to ROS 2 Bridge Node
# Path to the new config
    bridge_config = os.path.join(pkg_path, 'config', 'bridge.yaml')

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/model/my_robot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
        ],
        parameters=[{'config_file': bridge_config}],
        remappings=[
            ('/model/my_robot/tf', '/tf')
        ],
        output='screen'
    )

    # 4. Return everything to launch simultaneously
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot,
        # rviz2_node,
        # joint_state_publisher,
        ros_gz_bridge  
    ])