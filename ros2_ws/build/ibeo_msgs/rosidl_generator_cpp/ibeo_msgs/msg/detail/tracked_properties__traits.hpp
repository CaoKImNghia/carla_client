// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ibeo_msgs:msg/TrackedProperties.idl
// generated code does not contain a copyright notice

#ifndef IBEO_MSGS__MSG__DETAIL__TRACKED_PROPERTIES__TRAITS_HPP_
#define IBEO_MSGS__MSG__DETAIL__TRACKED_PROPERTIES__TRAITS_HPP_

#include "ibeo_msgs/msg/detail/tracked_properties__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'position_closest_point'
// Member 'relative_velocity'
// Member 'object_box_size'
// Member 'tracking_point_coordinate'
// Member 'velocity'
// Member 'acceleration'
#include "ibeo_msgs/msg/detail/point2_di__traits.hpp"
// Member 'relative_velocity_sigma'
// Member 'object_box_size_sigma'
// Member 'tracking_point_coordinate_sigma'
// Member 'velocity_sigma'
// Member 'acceleration_sigma'
#include "ibeo_msgs/msg/detail/point2_dui__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<ibeo_msgs::msg::TrackedProperties>()
{
  return "ibeo_msgs::msg::TrackedProperties";
}

template<>
inline const char * name<ibeo_msgs::msg::TrackedProperties>()
{
  return "ibeo_msgs/msg/TrackedProperties";
}

template<>
struct has_fixed_size<ibeo_msgs::msg::TrackedProperties>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<ibeo_msgs::msg::TrackedProperties>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<ibeo_msgs::msg::TrackedProperties>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // IBEO_MSGS__MSG__DETAIL__TRACKED_PROPERTIES__TRAITS_HPP_
