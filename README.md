# SUMMER-TASK-1
-Contain my learnings and screenshots of commands
## What is ROS 2?

ROS (Robot Operating System) is an open-source ecosystem that provides the framework, tools, and libraries for building, deploying, running, and maintaining robotic applications. This article introduces the main areas of the ecosystem and outlines their intended use.

### What are nodes?

Nodes are basically executable processes that performs one particular task in a robotic system. All nodes in a robotic system come together and form the robotic system itself, thus ros 2 splits functionality into smaller nodes. Here is the ros 2 graph, which visualizes the executables(talker and listener):

<img width="1535" height="308" alt="image" src="https://github.com/user-attachments/assets/4800d6ef-f74f-4437-8d5e-5ffe93e418f4" />

and here a ros 2 graph for visualising turtlesim:

<img width="1302" height="356" alt="image" src="https://github.com/user-attachments/assets/c44e183b-2bc3-450c-aa57-c14a465306dc" />

<img width="1328" height="814" alt="image" src="https://github.com/user-attachments/assets/03cba0e8-064c-4096-a53d-38a344138d45" />

### What are topics?

Topics are vital elements of ros graph and act as a bus for nodes to exchange messages. example of topic of type: geomentry_msgs/msg/Twist:-

<img width="1303" height="843" alt="image" src="https://github.com/user-attachments/assets/04807370-989d-4a05-bb7f-d56c3b9c8e9c" />



Usage of pub(publishing) command:

<img width="1315" height="608" alt="image" src="https://github.com/user-attachments/assets/90256e62-2cdd-4041-834e-1be864287b91" />



### What are services?

Services are another form of communication in ros2. They are based on call and response model.

For the service type: turtlesim/srv/Spawn: everything above the --- is request and below it is response.

Request

'---'

Response

<img width="841" height="187" alt="image" src="https://github.com/user-attachments/assets/d02356f4-01dd-4183-ad41-6ffc86f1fd61" />

example service call:

<img width="1033" height="692" alt="image" src="https://github.com/user-attachments/assets/53142be4-1621-44d7-a24e-3b101a44977d" />


### MAKING OF WORKSPACE:
-First we make directory called ros2_ws.

-Then we make subdirectory called src inside ros_ws. This is where we'll build the packages.

<img width="410" height="163" alt="image" src="https://github.com/user-attachments/assets/b0f318cd-8f84-4b8e-bc96-8cb2ba9a4ac7" />


## MAKING OF PACKAGES:
### 1)Python Package:-
i)Publisher


-Inside src we run this command to build python package

<img width="808" height="54" alt="image" src="https://github.com/user-attachments/assets/a6f6b677-5bd0-40cf-8985-05beae90184a" />

-Download example talker node from github.

<img width="808" height="73" alt="image" src="https://github.com/user-attachments/assets/34fda167-12e8-4b45-a6bc-866892907c44" />

[Code for publisher node](ros2_ws/src/py_pubsub/py_pubsub/publisher_member_function.py)

-Then update description, maintainer and license in package.xml and setup.py files, and add dependencies into package.xml. Depenedencies are the required modules which were used in the publisher code.

ii)Subscriber

-Similar to publisher, download example listener node.

[Code for subcriber node](ros2_ws/src/py_pubsub/py_pubsub/subscriber_member_function.py)

-Again update description, maintainer and license in package.xml setup.py files, and add dependencies.

### 2)C++ Package:-

i)Publisher

-Again we run this command to build cpp package.

<img width="808" height="73" alt="image" src="https://github.com/user-attachments/assets/a64f6180-4968-4622-a112-7b173c1781b2" />

-Download example talker node from github.

[Code for publisher node](ros2_ws/src/cpp_pubsub/src/publisher_member_function.cpp)

-Similar to the python packages, update [package.xml](ros2_ws/src/cpp_pubsub/package.xml) and [Cmakelists.txt](ros2_ws/src/cpp_pubsub/CMakeLists.txt)

ii)Subscriber

Similar to publisher, download example listener node.

[Code for subscriber node](ros2_ws/src/cpp_pubsub/src/subscriber_member_function.cpp)

-Update [package.xml](ros2_ws/src/cpp_pubsub/package.xml) and [Cmakelists.txt](ros2_ws/src/cpp_pubsub/CMakeLists.txt)

## SOME CLI COMMANDS ON PACKAGES

<img width="798" height="211" alt="image" src="https://github.com/user-attachments/assets/e6c279ea-dfc0-4542-a3e2-7c30482a3182" />


## turtle_patrol PACKAGE:

### Subtask A:-

--We create a package named turtle_patrol and node named collision_avoidance_node using these commands:

```
cd ~/ros2_ws/src/

mkdir turtle_patrol

cd ~/ros2_ws/src/turtle_patrol/turtle_patrol

touch collision_avoidance_node.py

```

--In this node we subscribe to /turtle1/pose topic of message type turtlesim/msg/Pose, which continuosly reads thr turtle's x, y and theta.

--In the same node we publish /turtle1/cmd_vel topic of message type geometry_msgs/msg/Twist.

--The purpose is to make the turtle move forward until it crosses a safety_threshold value which can be changed dynamically in the the cli. This safety_threshold value is the distance from any of the walls of a square of 11x11 dimensions, and when it is reached, turtle should turn away and in turn avoid collision with th wall.

--Code for this node: [collision_avoidance_node.py](ros2_ws/src/turtle_patrol/turtle_patrol/collision_avoidance_node.py)

--Logic: 

->move forward with some linear velocity and zero angular velocity.

->If x<safety_threshold or x>safety_threshold or y<safety_threshold or y>safety_threshold 












