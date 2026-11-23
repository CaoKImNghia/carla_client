// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ibeo_msgs:msg/UntrackedProperties.idl
// generated code does not contain a copyright notice

#ifndef IBEO_MSGS__MSG__DETAIL__UNTRACKED_PROPERTIES__TRAITS_HPP_
#define IBEO_MSGS__MSG__DETAIL__UNTRACKED_PROPERTIES__TRAITS_HPP_

#include "ibeo_msgs/msg/detail/untracked_properties__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'position_closest_point'
// Member 'object_box_size'
// Member 'tracking_point_coordinate'
#include "ibeo_msgs/msg/detail/point2_di__traits.hpp"
// Member 'object_box_size_sigma'
// Member 'tracking_point_coordinate_sigma'
#include "ibeo_msgs/msg/detail/point2_dui__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<ibeo_msgs::msg::UntrackedProperties>()
{
  return "ibeo_msgs::msg::UntrackedProperties";
}

template<>
inline const char * name<ibeo_msgs::msg::UntrackedProperties>()
{
  return "ibeo_msgs/msg/UntrackedProperties";
}

template<>
struct has_fixed_size<ibeo_msgs::msg::UntrackedProperties>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<ibeo_msgs::msg::UntrackedProperties>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<ibeo_msgs::msg::UntrackedProperties>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // IBEO_MSGS__MSG__DETAIL__UNTRACKED_PROPERTIES__TRAITS_HPP_
