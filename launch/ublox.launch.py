"""Lanza el GPS u-blox M8 real con los nombres de topic del resto del robot.

El nodo ublox_gps publica en ~/fix; aquí se remapea a `ublox/fix` (mismo patrón que
`sbg_ig500n/navsat/...` y `vectornav/imu`), de modo que `navsat_transform_node` lo pueda usar.

Argumentos:
  port       puerto serie (por defecto /dev/ublox, ver udev/99-ublox.rules)
  frame_id   frame del mensaje NavSatFix (por defecto gps_ublox_link)
  namespace  espacio de nombres (por defecto vacío)
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('caddy_ai2_ros2_sensors_gps_ublox')
    cfg = os.path.join(pkg, 'config', 'ublox_m8.yaml')

    node = Node(
        package='ublox_gps', executable='ublox_gps_node', name='ublox_gps_node',
        namespace=LaunchConfiguration('namespace'), output='both',
        parameters=[cfg, {
            'device': LaunchConfiguration('port'),
            'frame_id': LaunchConfiguration('frame_id'),
        }],
        remappings=[
            ('fix', 'ublox/fix'),
            ('fix_velocity', 'ublox/fix_velocity'),
            ('navpvt', 'ublox/navpvt'),
            ('navstatus', 'ublox/navstatus'),
            ('monhw', 'ublox/monhw'),
        ])

    return LaunchDescription([
        DeclareLaunchArgument('port', default_value='/dev/ublox'),
        DeclareLaunchArgument('frame_id', default_value='gps_ublox_link'),
        DeclareLaunchArgument('namespace', default_value=''),
        node,
        # Si el nodo muere (puerto desconectado), cerrar el launch para que systemd/el usuario lo vea.
        RegisterEventHandler(OnProcessExit(
            target_action=node, on_exit=[EmitEvent(event=Shutdown())])),
    ])
