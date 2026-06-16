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
    pkg_path = get_package_share_directory('robot')
    
    urdf_file = os.path.join(pkg_path, 'urdf', 'my_robot.urdf.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'my_world.sdf')
    rviz_config_path = os.path.join(pkg_path, 'rviz', 'urdf_config.rviz')
    controller_yaml = os.path.join(pkg_path, 'config', 'robot_controllers.yaml')

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

    # Spawner for Joint State Broadcaster (Delayed by 8 seconds)
    # MODIFIED: Added -c /my_robot/controller_manager to point to the simulator container
    joint_state_broadcaster = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_state_broadcaster', '-c', '/controller_manager'],
                output='screen'
            )
        ]
    )

    # Spawner for Arm Controller (Delayed by 10 seconds)
    # MODIFIED: Added -c /my_robot/controller_manager to point to the simulator container
    arm_controller = TimerAction(
        period=10.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['arm_controller', '-c', '/controller_manager'],
                output='screen'
            )
        ]
    )

    # RViz2 Node
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )

    joint_state_publisher=Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen'
    )
    # rqt_joint_trajectory_controller Node
    rqt_controller_node = Node(
        package='rqt_joint_trajectory_controller',
        executable='rqt_joint_trajectory_controller',
        output='screen'
    )

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
            
            # ─── REMAPPED THIS LINE TO CAPTURE THE NAMESPACED WHEEL TRANSFORMS ───
            '/model/my_robot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
        ],
        parameters=[{'config_file': bridge_config}],
        
        # ─── REMAP THE TOPIC SYSTEM-WIDE INSIDE ROS ───
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
        joint_state_broadcaster,
        arm_controller,
        rviz2_node,
        joint_state_publisher,
        rqt_controller_node,
        ros_gz_bridge  
    ])
