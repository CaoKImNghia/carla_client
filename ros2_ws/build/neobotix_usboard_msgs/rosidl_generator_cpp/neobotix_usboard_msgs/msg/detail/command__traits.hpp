// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from neobotix_usboard_msgs:msg/Command.idl
// generated code does not contain a copyright notice

#ifndef NEOBOTIX_USBOARD_MSGS__MSG__DETAIL__COMMAND__TRAITS_HPP_
#define NEOBOTIX_USBOARD_MSGS__MSG__DETAIL__COMMAND__TRAITS_HPP_

#include "neobotix_usboard_msgs/msg/detail/command__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<neobotix_usboard_msgs::msg::Command>()
{
  return "neobotix_usboard_msgs::msg::Command";
}

template<>
inline const char * name<neobotix_usboard_msgs::msg::Command>()
{
  return "neobotix_usboard_msgs/msg/Command";
}

template<>
struct has_fixed_size<neobotix_usboard_msgs::msg::Command>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<neobotix_usboard_msgs::msg::Command>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<neobotix_usboard_msgs::msg::Command>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // NEOBOTIX_USBOARD_MSGS__MSG__DETAIL__COMMAND__TRAITS_HPP_
