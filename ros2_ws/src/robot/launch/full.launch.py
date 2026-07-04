import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, AppendEnvironmentVariable  # <-- Added AppendEnvironmentVariable
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
import xacro

def generate_launch_description():

    # 1. Paths Setup
    pkg_path = get_package_share_directory('robot')
    
    urdf_file = os.path.join(pkg_path, 'urdf', 'my_robot.urdf.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'my_world.sdf')
    rviz_config_path = os.path.join(pkg_path, 'rviz', 'urdf_config.rviz')
    controller_yaml = os.path.join(pkg_path, 'config', 'robot_controllers.yaml')

    # 2. Environment Setup for ArUco Marker textures
    set_gz_resource_path = AppendEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.join(pkg_path, 'models')
    )

    # 3. Process Xacro to get robot_description
    robot_description_config = xacro.process_file(urdf_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    # 4. Nodes & Processes definitions

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

    # Spawn ArUco Marker into Gazebo (Delayed by 5 seconds alongside the robot)
# ─── READ AND PREPARE THE DYNAMIC MATERIAL STRINGS ───


# ─── SIMPLIFIED SPAWNER ───
    spawn_aruco_markers = TimerAction(
        period=5.0,
        actions=[
            # Spawn Instance A (Reads directly from original folder -> loads marker_0.png)
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-file', os.path.join(pkg_path, 'models', 'aruco_marker', 'model.sdf'),
                    '-name', 'marker_instance_A',
                    '-x', '2.5', '-y', '-0.5', '-z', '1.0',
                    '-R', '0.0', '-P', '1.5708', '-Y', '0.0'
                ],
                output='screen'
            ),
            # Spawn Instance B (Reads directly from second folder -> loads marker_1.png)
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-file', os.path.join(pkg_path, 'models', 'aruco_marker_id1', 'model.sdf'),
                    '-name', 'marker_instance_B',
                    '-x', '2.5', '-y', '0.5', '-z', '1.0',
                    '-R', '0.0', '-P', '1.5708', '-Y', '0.0'
                ],
                output='screen'
            ),
        ]
    )
    # Spawner for Joint State Broadcaster (Delayed by 8 seconds)
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

    joint_state_publisher = Node(
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
                '/model/my_robot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                '/model/my_robot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                
                # ─── ADD THIS: JOINT STATE BRIDGE ENTRY ───
                '/model/my_robot/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model'
            ],
            parameters=[{'config_file': bridge_config}],
            remappings=[
                ('/model/my_robot/tf', '/tf'),
                ('/model/my_robot/odometry', '/odom'),
                
                # ─── ADD THIS: REMAP TO STANDARD FLAT /joint_states ───
                ('/model/my_robot/joint_state', '/joint_states')
            ],
            output='screen'
    )
    aruco_tracker_node = Node(
        package='robot',
        executable='aruco_tracker',
        parameters=[{'use_sim_time': True}], # <-- CRUCIAL FOR TF SYNC
        output='screen'
    )

    # 5. Return everything to launch simultaneously
    return LaunchDescription([
        set_gz_resource_path, # Environment variable loaded first
        gazebo,
        robot_state_publisher,
        spawn_robot,
        spawn_aruco_markers,   # Spawns ArUco markers
        joint_state_broadcaster,
        rviz2_node,
        arm_controller,
        joint_state_publisher,
        rqt_controller_node,
        ros_gz_bridge,
        aruco_tracker_node
    ])