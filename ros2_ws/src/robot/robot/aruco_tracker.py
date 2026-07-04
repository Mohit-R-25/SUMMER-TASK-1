import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
import tf2_ros # Modern dynamic broadcaster
from cv_bridge import CvBridge
import cv2
import numpy as np

class UltimateArucoTracker(Node):
    def __init__(self):
        super().__init__('aruco_tracker_node')
        
        self.set_parameters([rclpy.parameter.Parameter('use_sim_time', rclpy.parameter.Parameter.Type.BOOL, True)])
        
        self.bridge = CvBridge()
        self.tracked_markers = {}   # Database: { marker_id: [x, y, z] }
        self.alpha = 0.15          # Jitter low-pass filter weight
        self.dist_threshold = 0.30 # Spatial proximity gate (30 cm)

        # UPGRADED: Dynamic broadcaster lets multiple unique frames coexist perfectly
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # Robot Odometry Cache
        self.robot_x, self.robot_y, self.robot_z = 0.0, 0.0, 0.0

        # ArUco Config (Matched to your verified 5x5 Gazebo asset)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        self.marker_length = 0.3 

        # Topics
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        self.cam_info_sub = self.create_subscription(CameraInfo, '/camera/camera_info', self.cam_info_cb, 10)
        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_cb, 10)
        
        self.k_matrix = None
        self.d_coeff = None

    def odom_cb(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        self.robot_z = msg.pose.pose.position.z

    def cam_info_cb(self, msg):
        self.k_matrix = np.array(msg.k, dtype=np.float64).reshape((3, 3))
        self.d_coeff = np.array(msg.d, dtype=np.float64)

    def image_cb(self, msg):
        # 1.Ensure we have camera calibration matrices before running detection
        if self.k_matrix is None:
            return

        # 2.Convert incoming ROS 2 image message to OpenCV format
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # 3.Detect the markers in a single pass (Uses self.detector set to DICT_5X5_50)
        corners, ids, _ = self.detector.detectMarkers(gray)
        
        # 4. Process matches if any markers are in the camera's FOV
        if ids is not None:
            # Estimate 3D spatial pose (rvecs = rotation vectors, tvecs = translation vectors)
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, 
                float(self.marker_length), 
                self.k_matrix, 
                self.d_coeff
            )
            
            # Loop through all detected markers simultaneously
            for i, marker_id in enumerate(ids.flatten()):
                # Pass the unique marker ID, its coordinate vector, and the exact clock timestamp
                self.calculate_global_marker(marker_id, tvecs[i][0], msg.header.stamp)

    def calculate_global_marker(self, marker_id, tvec, timestamp):
        cam_x, cam_y, cam_z = tvec[0], tvec[1], tvec[2]

        global_x = self.robot_x + cam_z
        global_y = self.robot_y - cam_x
        global_z = self.robot_z - cam_y

        # ─── DIAGNOSTIC 2: Filter evaluation tracking ───
        if marker_id in self.tracked_markers:
            prev_x, prev_y, prev_z = self.tracked_markers[marker_id]
            distance = np.sqrt((global_x - prev_x)**2 + (global_y - prev_y)**2 + (global_z - prev_z)**2)

            if distance < self.dist_threshold:
                global_x = self.alpha * global_x + (1 - self.alpha) * prev_x
                global_y = self.alpha * global_y + (1 - self.alpha) * prev_y
                global_z = self.alpha * global_z + (1 - self.alpha) * prev_z
            else:
                self.get_logger().warn(f"ID {marker_id} dropped by distance noise filter! Jumped {distance:.2f}m")
                return

        self.tracked_markers[marker_id] = [global_x, global_y, global_z]
        
        # ─── DIAGNOSTIC 3: Confirm it cleared all gates ───
        self.get_logger().info(f"Publishing TF Frame for marker_{marker_id} at [{global_x:.2f}, {global_y:.2f}]")

        t = TransformStamped()
        t.header.stamp = timestamp
        t.header.frame_id = 'odom'
        t.child_frame_id = f'aruco_marker_{marker_id}'
        t.transform.translation.x = global_x
        t.transform.translation.y = global_y
        t.transform.translation.z = global_z
        t.transform.rotation.w = 1.0 
        
        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = UltimateArucoTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()