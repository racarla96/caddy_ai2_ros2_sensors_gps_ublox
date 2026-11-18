cmake_minimum_required(VERSION 3.8)
project(caddy_ai2_ros2_sensors_gps_ublox)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch udev description bringup
  DESTINATION share/${PROJECT_NAME})

ament_package()
