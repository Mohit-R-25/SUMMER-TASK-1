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



