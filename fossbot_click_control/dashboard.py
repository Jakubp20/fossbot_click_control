import threading
from collections import deque

import matplotlib.pyplot as plt
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class Dashboard(Node):
    def __init__(self):
        super().__init__('dashboard')

        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('history_length', 300)
        self.declare_parameter('trajectory_length', 3000)
        self.declare_parameter('sample_rate', 10.0)

        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        odom_topic = self.get_parameter('odom_topic').value
        history = self.get_parameter('history_length').value
        trajectory = self.get_parameter('trajectory_length').value
        rate = self.get_parameter('sample_rate').value

        self.cmd_speed = 0.0
        self.odom_speed = 0.0
        self.x = None
        self.y = None
        self.start_time = None

        self.lock = threading.Lock()
        self.times = deque(maxlen=history)
        self.cmd_history = deque(maxlen=history)
        self.odom_history = deque(maxlen=history)
        self.path_x = deque(maxlen=trajectory)
        self.path_y = deque(maxlen=trajectory)

        self.create_subscription(Twist, cmd_vel_topic, self.cmd_callback, 10)
        self.create_subscription(Odometry, odom_topic, self.odom_callback, 10)
        self.create_timer(1.0 / rate, self.sample)

        self.get_logger().info(f'Plotting {cmd_vel_topic} and {odom_topic}')

    def cmd_callback(self, msg):
        self.cmd_speed = msg.linear.x

    def odom_callback(self, msg):
        self.odom_speed = msg.twist.twist.linear.x
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    def sample(self):
        now = self.get_clock().now().nanoseconds / 1e9
        if now == 0.0:
            return
        if self.start_time is None:
            self.start_time = now

        with self.lock:
            self.times.append(now - self.start_time)
            self.cmd_history.append(self.cmd_speed)
            self.odom_history.append(self.odom_speed)
            if self.x is not None:
                self.path_x.append(self.x)
                self.path_y.append(self.y)

    def get_velocity_history(self):
        with self.lock:
            return list(self.times), list(self.cmd_history), list(self.odom_history)

    def get_trajectory(self):
        with self.lock:
            return list(self.path_x), list(self.path_y)


def spin_in_background(node):
    try:
        rclpy.spin(node)
    except ExternalShutdownException:
        pass


def update_velocity_plot(ax, cmd_line, odom_line, times, cmd, odom):
    cmd_line.set_data(times, cmd)
    odom_line.set_data(times, odom)
    ax.relim()
    ax.autoscale_view()
    low, high = ax.get_ylim()
    ax.set_ylim(min(low, -0.3), max(high, 0.3))


def update_trajectory_plot(ax, path_line, robot_dot, xs, ys):
    path_line.set_data(xs, ys)
    robot_dot.set_data([xs[-1]], [ys[-1]])

    center_x = (min(xs) + max(xs)) / 2
    center_y = (min(ys) + max(ys)) / 2
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
    half = span / 2 + 0.2
    ax.set_xlim(center_x - half, center_x + half)
    ax.set_ylim(center_y - half, center_y + half)


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = Dashboard()
    spin_thread = threading.Thread(target=spin_in_background, args=(node,), daemon=True)
    spin_thread.start()

    plt.ion()
    fig, (ax_vel, ax_traj) = plt.subplots(1, 2, figsize=(12, 4.5))
    fig.canvas.manager.set_window_title('FOSSBot dashboard')

    cmd_line, = ax_vel.plot([], [], linewidth=3, label='commanded (/cmd_vel)')
    odom_line, = ax_vel.plot([], [], linestyle='--', label='measured (/odom)')
    ax_vel.set_title('Linear velocity')
    ax_vel.set_xlabel('time [s]')
    ax_vel.set_ylabel('velocity [m/s]')
    ax_vel.grid(True)
    ax_vel.legend(loc='upper right')

    path_line, = ax_traj.plot([], [], label='path')
    robot_dot, = ax_traj.plot([], [], 'o', color='red', label='robot')
    ax_traj.set_title('Trajectory (/odom)')
    ax_traj.set_xlabel('x [m]')
    ax_traj.set_ylabel('y [m]')
    ax_traj.set_aspect('equal', adjustable='box')
    ax_traj.grid(True)
    ax_traj.legend(loc='upper right')

    fig.tight_layout()

    try:
        while rclpy.ok() and plt.fignum_exists(fig.number):
            times, cmd, odom = node.get_velocity_history()
            if times:
                update_velocity_plot(ax_vel, cmd_line, odom_line, times, cmd, odom)

            xs, ys = node.get_trajectory()
            if xs:
                update_trajectory_plot(ax_traj, path_line, robot_dot, xs, ys)

            plt.pause(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.try_shutdown()
        spin_thread.join(timeout=1.0)
        node.destroy_node()
        plt.close('all')