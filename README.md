# fossbot_click_control

ROS 2 (Jazzy) package for controlling the [FOSSBot](https://github.com/LRMPUT/FOSSBotEduSim) robot by clicking in a camera window.

- Click above the centre line: the robot drives forward.
- Click below the centre line: the robot drives backward.
- The robot stops automatically after a set time.

## Nodes

- `click_controller`: shows the camera image (`/camera/image_raw`) and publishes velocity commands on `/cmd_vel` after a click.
- `dashboard`: live plots of linear velocity (`/cmd_vel`, `/odom`) and robot trajectory (`/odom`).

## Installation

Requires [FOSSBotEduSim](https://github.com/LRMPUT/FOSSBotEduSim) (Docker image with ROS 2 Jazzy and the simulation).

```bash
git clone https://github.com/LRMPUT/FOSSBotEduSim
cd FOSSBotEduSim
bash build_image.sh
cd ws_fossbot/src
git clone https://github.com/Jakubp20/fossbot_click_control.git
```

Start the container and build the package:

```bash
cd FOSSBotEduSim
bash start_container.sh
cd /fossbot_ros2/ws_fossbot
colcon build --packages-select fossbot_click_control
```

## Running

Every new terminal:

```bash
docker exec -it ros2_fossbot_edu bash
cd /fossbot_ros2/ws_fossbot
source install/setup.bash
```

1. Simulation (robot and camera):

   ```bash
   ros2 launch fossbot_educational_description single.launch.py world:=simple_shapes.sdf
   ```

2. Control interface and dashboard:

   ```bash
   ros2 launch fossbot_click_control click_control.launch.py
   ```

### Launch arguments

| Argument | Default | Description |
|---|---|---|
| `use_sim_time` | `true` | Use the simulation clock |
| `image_topic` | `/camera/image_raw` | Camera image topic |
| `linear_speed` | `0.2` | Speed after a click [m/s] |
| `move_duration` | `2.0` | Movement time after a click [s] |

Example: `ros2 launch fossbot_click_control click_control.launch.py linear_speed:=0.4`

## Author

Jakub Piwosz ([@Jakubp20](https://github.com/Jakubp20))
