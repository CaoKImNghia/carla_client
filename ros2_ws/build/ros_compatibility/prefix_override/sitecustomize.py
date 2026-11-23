import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/enovonck2004/carla_client/ros2_ws/install/ros_compatibility'
