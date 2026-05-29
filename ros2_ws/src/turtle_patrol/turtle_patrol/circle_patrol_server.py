#!/usr/bin/env python3
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from turtle_patrol.action import ExecuteCircle


class CirclePatrolServer(Node):

    def __init__(self):

        super().__init__('circle_patrol_server')

        self.current_pose = None

        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self._action_server = ActionServer(
            self,
            ExecuteCircle,
            'execute_circle',
            self.execute_callback
        )

        self.get_logger().info(
            'Circle Patrol Server Started'
        )

    def pose_callback(self, msg):

        self.current_pose = msg

    async def execute_callback(self, goal_handle):

        self.get_logger().info(
            'Executing circle patrol...'
        )

        radius = goal_handle.request.radius

        result = ExecuteCircle.Result()

        # Validate radius
        if radius <= 0.0:

            result.success = False
            result.final_report = 'Invalid radius'

            goal_handle.abort()

            return result

        # Wait until pose is received
        while self.current_pose is None:
            time.sleep(0.1)

        # Fixed linear velocity
        linear_speed = 1.5

        # Angular velocity calculation
        angular_speed = linear_speed / radius

        # Store starting position
        start_x = self.current_pose.x
        start_y = self.current_pose.y

        # Distance tracking
        distance_traveled = 0.0

        # Detect whether turtle left start area
        has_left_start = False

        # Time tracking
        previous_time = time.time()

        # Velocity command
        twist = Twist()
        twist.linear.x = linear_speed
        twist.angular.z = angular_speed

        feedback_msg = ExecuteCircle.Feedback()

        while rclpy.ok():

            # Publish movement command
            self.publisher_.publish(twist)

            # Time difference
            current_time = time.time()

            dt = current_time - previous_time

            previous_time = current_time

            # Arc length distance
            distance_traveled += linear_speed * dt

            # Publish feedback
            feedback_msg.distance_traveled = (
                distance_traveled
            )

            feedback_msg.current_status = (
                'Patrolling'
            )

            goal_handle.publish_feedback(
                feedback_msg
            )

            # Current position
            x = self.current_pose.x
            y = self.current_pose.y

            # Boundary collision detection
            if (
                x < 1.0 or
                x > 10.0 or
                y < 1.0 or
                y > 10.0
            ):

                stop_msg = Twist()

                self.publisher_.publish(stop_msg)

                result.success = False

                result.final_report = (
                    'Mission Aborted: Boundary Collision Imminent!'
                )

                goal_handle.abort()

                self.get_logger().info(
                    result.final_report
                )

                return result

            # Distance from starting point
            distance_from_start = math.sqrt(
                (x - start_x) ** 2 +
                (y - start_y) ** 2
            )

            # Detect whether turtle moved away
            if distance_from_start > 1.0:
                has_left_start = True

            # Check full circle completion
            if (
                has_left_start and
                distance_from_start < 0.2
            ):

                stop_msg = Twist()

                self.publisher_.publish(stop_msg)

                result.success = True

                result.final_report = (
                    'Full circle completed successfully!'
                )

                goal_handle.succeed()

                self.get_logger().info(
                    result.final_report
                )

                return result

            time.sleep(0.05)


def main(args=None):

    rclpy.init(args=args)

    node = CirclePatrolServer()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()