// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ibeo_msgs:msg/Object2225.idl
// generated code does not contain a copyright notice

#ifndef IBEO_MSGS__MSG__DETAIL__OBJECT2225__TRAITS_HPP_
#define IBEO_MSGS__MSG__DETAIL__OBJECT2225__TRAITS_HPP_

#include "ibeo_msgs/msg/detail/object2225__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'timestamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"
// Member 'bounding_box_center'
// Member 'bounding_box_size'
// Member 'object_box_center'
// Member 'object_box_center_sigma'
// Member 'object_box_size'
// Member 'relative_velocity'
// Member 'relative_velocity_sigma'
// Member 'absolute_velocity'
// Member 'absolute_velocity_sigma'
#include "ibeo_msgs/msg/detail/point2_df__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<ibeo_msgs::msg::Object2225>()
{
  return "ibeo_msgs::msg::Object2225";
}

template<>
inline const char * name<ibeo_msgs::msg::Object2225>()
{
  return "ibeo_msgs/msg/Object2225";
}

template<>
struct has_fixed_size<ibeo_msgs::msg::Object2225>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<ibeo_msgs::msg::Object2225>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<ibeo_msgs::msg::Object2225>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // IBEO_MSGS__MSG__DETAIL__OBJECT2225__TRAITS_HPP_
