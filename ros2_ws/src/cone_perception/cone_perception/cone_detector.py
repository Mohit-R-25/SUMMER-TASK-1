#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class ConeDetectorNode(Node):
    def __init__(self):
        super().__init__('cone_detector')
        
        # 1. Load your new augmented weights
        # Replace this path with the exact location of your weights file
        self.model = YOLO('/home/mohit/ros2_ws/src/cone_perception/best_augmented.pt')
        
        self.bridge = CvBridge()
        
        # 2. Change this topic to match your Gazebo camera topic exactly
        # Common ones: '/camera/image_raw', '/camera/image_compat', '/intel_realsense_r200_depth/image_raw'
        self.camera_topic = '/camera/image_raw'
        
        self.subscription = self.create_subscription(
            Image,
            self.camera_topic,
            self.image_callback,
            10)
            
        self.get_logger().info(f'YOLO Cone Detector started. Subscribed to {self.camera_topic}')

    def image_callback(self, msg):
        try:
            # Convert ROS Image message to standard OpenCV BGR image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {str(e)}')
            return

        # Run inference (stream=True keeps memory usage low during live video)
        results = self.model(cv_image, conf=0.4, verbose=False, stream=True)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Extract bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                class_name = result.names[cls]
                
                # Log the live coordinate positions to your terminal
                self.get_logger().info(f'Found {class_name} ({conf:.2f}) at Box: [{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]')
                
                # Draw visual feedback box directly onto the frame
                cv2.rectangle(cv_image, (int(x1), \
                              int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(cv_image, f'{class_name} {conf:.2f}', (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Display the live inference feedback stream window
        cv2.imshow("Gazebo Live YOLO Detections", cv_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ConeDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()