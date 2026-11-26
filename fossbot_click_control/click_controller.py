import cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class ClickController(Node):
    def __init__(self):
        super().__init__('click_controller')

        self.declare_parameter('image_topic', '/camera/image_raw')
        image_topic = self.get_parameter('image_topic').value

        self.bridge = CvBridge()
        self.frame = None
        self.window_name = 'FOSSBot click control'

        self.create_subscription(
            Image, image_topic, self.image_callback, qos_profile_sensor_data)
        self.create_timer(1.0 / 30.0, self.gui_loop)

        cv2.namedWindow(self.window_name)
        self.get_logger().info(f'Listening for images on {image_topic}')

    def image_callback(self, msg):
        self.frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    def gui_loop(self):
        if self.frame is not None:
            display = self.frame.copy()
            h, w = display.shape[:2]
            cv2.line(display, (0, h // 2), (w, h // 2), (0, 255, 255), 1)
            cv2.imshow(self.window_name, display)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ClickController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.try_shutdown()