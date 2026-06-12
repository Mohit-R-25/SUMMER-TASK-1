import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
import xacro

def generate_launch_description():

    # Paths Setup
    pkg_path = get_package_share_directory('robot')
    
    urdf_file = os.path.join(pkg_path, 'urdf', 'my_robot.urdf.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'my_world.sdf')
    rviz_config_path = os.path.join(pkg_path, 'rviz', 'urdf_config.rviz')
    controller_yaml = os.path.join(pkg_path, 'config', 'robot_controllers.yaml')

    # Process Xacro to get robot_description
    robot_description_config = xacro.process_file(urdf_file)
    robot_description = {'robot_description': robot_description_config.toxml()}


    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', world_file],
        output='screen'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description],
        output='screen'
    )

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

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[robot_description, controller_yaml],
        output='screen'
    )

    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    arm_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller'],
        output='screen'
    )

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )

    rqt_controller_node = Node(
        package='rqt_joint_trajectory_controller',
        executable='rqt_joint_trajectory_controller',
        output='screen'
    )

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            # --- Added IMU and LiDAR Bridges ---
            '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        output='screen'
    )

    # Optional: Joint State Publisher GUI (Uncomment if you aren't using Gazebo physics/control)
    # joint_state_publisher_gui_node = Node(
    #     package='joint_state_publisher_gui',
    #     executable='joint_state_publisher_gui'
    # )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot,
        controller_manager,
        joint_state_broadcaster,
        arm_controller,
        rviz2_node,
        rqt_controller_node,
        ros_gz_bridge  # Active bridge node
        # joint_state_publisher_gui_node 
    ])