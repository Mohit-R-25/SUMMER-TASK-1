cmake_minimum_required(VERSION 3.8)
project(turtle_patrol)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/ExecuteCircle.action"
)

install(PROGRAMS
  turtle_patrol/collision_avoidance_node.py
  turtle_patrol/circle_patrol_server.py
  turtle_patrol/circle_patrol_client.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()