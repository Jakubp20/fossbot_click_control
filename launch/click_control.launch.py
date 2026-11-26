from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    image_topic = LaunchConfiguration('image_topic')
    linear_speed = LaunchConfiguration('linear_speed')
    move_duration = LaunchConfiguration('move_duration')

    sim_time_param = ParameterValue(use_sim_time, value_type=bool)

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the simulation clock (/clock)'),
        DeclareLaunchArgument(
            'image_topic', default_value='/camera/image_raw',
            description='Topic with camera images'),
        DeclareLaunchArgument(
            'linear_speed', default_value='0.2',
            description='Robot speed after a click [m/s]'),
        DeclareLaunchArgument(
            'move_duration', default_value='2.0',
            description='How long the robot moves after a click [s]'),

        Node(
            package='fossbot_click_control',
            executable='click_controller',
            name='click_controller',
            output='screen',
            parameters=[{
                'use_sim_time': sim_time_param,
                'image_topic': image_topic,
                'cmd_vel_topic': '/cmd_vel',
                'linear_speed': ParameterValue(linear_speed, value_type=float),
                'move_duration': ParameterValue(move_duration, value_type=float),
            }],
        ),

        Node(
            package='fossbot_click_control',
            executable='dashboard',
            name='dashboard',
            output='screen',
            parameters=[{
                'use_sim_time': sim_time_param,
                'cmd_vel_topic': '/cmd_vel',
                'odom_topic': '/odom',
                'history_length': 300,
                'trajectory_length': 3000,
                'sample_rate': 10.0,
            }],
        ),
    ])