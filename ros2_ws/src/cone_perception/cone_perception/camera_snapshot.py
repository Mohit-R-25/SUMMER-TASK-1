import os
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class CameraSnapshotNode(Node):
    def __init__(self):
        super().__init__('camera_snapshot_node')
        
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw', 
            self.image_callback,
            10)
            
        self.bridge = CvBridge()
        self.latest_frame = None
        
        # Output directory for images
        self.save_path = os.path.expanduser('~/ros2_ws/src/cone_perception/worlds/dataset/')
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
            
        # ─── FIX: SCAN THE FOLDER FOR EXISTING IMAGES ───
        # This looks at the folder, filters for files starting with 'cone_frame_', and sets the starting index
        existing_files = [f for f in os.listdir(self.save_path) if f.startswith('cone_frames_') and f.endswith('.png')]
        
        if existing_files:
            # Extract numbers from filenames like 'cone_frame_27.png' to find the absolute maximum
            file_numbers = []
            for f in existing_files:
                try:
                    num = int(f.replace('cone_frames_', '').replace('.png', ''))
                    file_numbers.append(num)
                except ValueError:
                    pass
            self.img_counter = max(file_numbers) + 1 if file_numbers else 0
        else:
            self.img_counter = 0
            
        self.get_logger().info(f"Snapshot node started. Resuming save index from: cone_frames_{self.img_counter}.png")
        self.get_logger().info("Press 's' in the OpenCV window to save an image, or 'q' to quit.")

    def image_callback(self, msg):
        try:
            # Convert ROS 2 Image message to OpenCV image
            self.latest_frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Display live camera stream
            cv2.imshow("Robot Camera View", self.latest_frame)
            key = cv2.waitKey(1) & 0xFF
            
            # Press 's' to save the frame
            if key == ord('s'):
                img_name = os.path.join(self.save_path, f"cone_frames_{self.img_counter}.png")
                cv2.imwrite(img_name, self.latest_frame)
                self.get_logger().info(f"Saved: {img_name}")
                self.img_counter += 1
            elif key == ord('q'):
                self.get_logger().info("Shutting down node...")
                rclpy.shutdown()
                
        except Exception as e:
            self.get_logger().error(f"Failed to process image: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = CameraSnapshotNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()

if __name__ == '__main__':
    main()