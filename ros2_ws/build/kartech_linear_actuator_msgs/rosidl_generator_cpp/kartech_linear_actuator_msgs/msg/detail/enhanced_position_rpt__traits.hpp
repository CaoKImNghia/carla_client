// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from kartech_linear_actuator_msgs:msg/EnhancedPositionRpt.idl
// generated code does not contain a copyright notice

#ifndef KARTECH_LINEAR_ACTUATOR_MSGS__MSG__DETAIL__ENHANCED_POSITION_RPT__TRAITS_HPP_
#define KARTECH_LINEAR_ACTUATOR_MSGS__MSG__DETAIL__ENHANCED_POSITION_RPT__TRAITS_HPP_

#include "kartech_linear_actuator_msgs/msg/detail/enhanced_position_rpt__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<kartech_linear_actuator_msgs::msg::EnhancedPositionRpt>()
{
  return "kartech_linear_actuator_msgs::msg::EnhancedPositionRpt";
}

template<>
inline const char * name<kartech_linear_actuator_msgs::msg::EnhancedPositionRpt>()
{
  return "kartech_linear_actuator_msgs/msg/EnhancedPositionRpt";
}

template<>
struct has_fixed_size<kartech_linear_actuator_msgs::msg::EnhancedPositionRpt>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<kartech_linear_actuator_msgs::msg::EnhancedPositionRpt>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<kartech_linear_actuator_msgs::msg::EnhancedPositionRpt>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // KARTECH_LINEAR_ACTUATOR_MSGS__MSG__DETAIL__ENHANCED_POSITION_RPT__TRAITS_HPP_
