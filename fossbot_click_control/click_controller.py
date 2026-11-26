import cv2
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

LINEAR_SPEED = 0.2   # m/s
MOVE_DURATION = 2.0  # s


class ClickController(Node):
    def __init__(self):
        super().__init__('click_controller')

        self.declare_parameter('image_topic', '/camera/image_raw')
        image_topic = self.get_parameter('image_topic').value

        self.bridge = CvBridge()
        self.frame = None
        self.window_name = 'FOSSBot click control'

        self.current_speed = 0.0
        self.move_end_time = None
        self.last_click = None

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(
            Image, image_topic, self.image_callback, qos_profile_sensor_data)
        self.create_timer(1.0 / 30.0, self.gui_loop)
        self.create_timer(0.1, self.control_loop)

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.on_mouse)
        self.get_logger().info(f'Listening for images on {image_topic}')

    def image_callback(self, msg):
        self.frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    def on_mouse(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN or self.frame is None:
            return

        height = self.frame.shape[0]
        if y < height / 2:
            self.current_speed = LINEAR_SPEED
            direction = 'forward'
        else:
            self.current_speed = -LINEAR_SPEED
            direction = 'backward'

        self.move_end_time = self.get_clock().now() + Duration(seconds=MOVE_DURATION)
        self.last_click = (x, y)
        self.get_logger().info(f'Click at ({x}, {y}) -> {direction}')

    def control_loop(self):
        if self.move_end_time is None:
            return
        if self.get_clock().now() < self.move_end_time:
            self.publish_speed(self.current_speed)
        else:
            self.stop_robot()
            self.get_logger().info('Stop')

    def publish_speed(self, linear_x):
        msg = Twist()
        msg.linear.x = linear_x
        self.cmd_pub.publish(msg)

    def stop_robot(self):
        self.publish_speed(0.0)
        self.current_speed = 0.0
        self.move_end_time = None

    def gui_loop(self):
        if self.frame is not None:
            display = self.frame.copy()
            h, w = display.shape[:2]
            cv2.line(display, (0, h // 2), (w, h // 2), (0, 255, 255), 1)

            if self.last_click is not None:
                cv2.circle(display, self.last_click, 6, (0, 0, 255), 2)

            if self.current_speed > 0:
                status = 'FORWARD'
            elif self.current_speed < 0:
                status = 'BACKWARD'
            else:
                status = 'STOPPED'
            cv2.putText(display, status, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow(self.window_name, display)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = ClickController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.try_shutdown()