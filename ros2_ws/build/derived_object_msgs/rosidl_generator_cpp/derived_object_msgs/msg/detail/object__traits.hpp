// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from derived_object_msgs:msg/Object.idl
// generated code does not contain a copyright notice

#ifndef DERIVED_OBJECT_MSGS__MSG__DETAIL__OBJECT__TRAITS_HPP_
#define DERIVED_OBJECT_MSGS__MSG__DETAIL__OBJECT__TRAITS_HPP_

#include "derived_object_msgs/msg/detail/object__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__traits.hpp"
// Member 'twist'
#include "geometry_msgs/msg/detail/twist__traits.hpp"
// Member 'accel'
#include "geometry_msgs/msg/detail/accel__traits.hpp"
// Member 'polygon'
#include "geometry_msgs/msg/detail/polygon__traits.hpp"
// Member 'shape'
#include "shape_msgs/msg/detail/solid_primitive__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<derived_object_msgs::msg::Object>()
{
  return "derived_object_msgs::msg::Object";
}

template<>
inline const char * name<derived_object_msgs::msg::Object>()
{
  return "derived_object_msgs/msg/Object";
}

template<>
struct has_fixed_size<derived_object_msgs::msg::Object>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::Accel>::value && has_fixed_size<geometry_msgs::msg::Polygon>::value && has_fixed_size<geometry_msgs::msg::Pose>::value && has_fixed_size<geometry_msgs::msg::Twist>::value && has_fixed_size<shape_msgs::msg::SolidPrimitive>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<derived_object_msgs::msg::Object>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::Accel>::value && has_bounded_size<geometry_msgs::msg::Polygon>::value && has_bounded_size<geometry_msgs::msg::Pose>::value && has_bounded_size<geometry_msgs::msg::Twist>::value && has_bounded_size<shape_msgs::msg::SolidPrimitive>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<derived_object_msgs::msg::Object>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DERIVED_OBJECT_MSGS__MSG__DETAIL__OBJECT__TRAITS_HPP_
