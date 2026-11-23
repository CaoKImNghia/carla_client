// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from neobotix_usboard_msgs:msg/SensorData.idl
// generated code does not contain a copyright notice

#ifndef NEOBOTIX_USBOARD_MSGS__MSG__DETAIL__SENSOR_DATA__TRAITS_HPP_
#define NEOBOTIX_USBOARD_MSGS__MSG__DETAIL__SENSOR_DATA__TRAITS_HPP_

#include "neobotix_usboard_msgs/msg/detail/sensor_data__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<neobotix_usboard_msgs::msg::SensorData>()
{
  return "neobotix_usboard_msgs::msg::SensorData";
}

template<>
inline const char * name<neobotix_usboard_msgs::msg::SensorData>()
{
  return "neobotix_usboard_msgs/msg/SensorData";
}

template<>
struct has_fixed_size<neobotix_usboard_msgs::msg::SensorData>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<neobotix_usboard_msgs::msg::SensorData>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<neobotix_usboard_msgs::msg::SensorData>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // NEOBOTIX_USBOARD_MSGS__MSG__DETAIL__SENSOR_DATA__TRAITS_HPP_
