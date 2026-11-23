// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from derived_object_msgs:msg/ObjectWithCovariance.idl
// generated code does not contain a copyright notice

#ifndef DERIVED_OBJECT_MSGS__MSG__DETAIL__OBJECT_WITH_COVARIANCE__TRAITS_HPP_
#define DERIVED_OBJECT_MSGS__MSG__DETAIL__OBJECT_WITH_COVARIANCE__TRAITS_HPP_

#include "derived_object_msgs/msg/detail/object_with_covariance__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_with_covariance__traits.hpp"
// Member 'twist'
#include "geometry_msgs/msg/detail/twist_with_covariance__traits.hpp"
// Member 'accel'
#include "geometry_msgs/msg/detail/accel_with_covariance__traits.hpp"
// Member 'polygon'
#include "geometry_msgs/msg/detail/polygon__traits.hpp"
// Member 'shape'
#include "derived_object_msgs/msg/detail/solid_primitive_with_covariance__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<derived_object_msgs::msg::ObjectWithCovariance>()
{
  return "derived_object_msgs::msg::ObjectWithCovariance";
}

template<>
inline const char * name<derived_object_msgs::msg::ObjectWithCovariance>()
{
  return "derived_object_msgs/msg/ObjectWithCovariance";
}

template<>
struct has_fixed_size<derived_object_msgs::msg::ObjectWithCovariance>
  : std::integral_constant<bool, has_fixed_size<derived_object_msgs::msg::SolidPrimitiveWithCovariance>::value && has_fixed_size<geometry_msgs::msg::AccelWithCovariance>::value && has_fixed_size<geometry_msgs::msg::Polygon>::value && has_fixed_size<geometry_msgs::msg::PoseWithCovariance>::value && has_fixed_size<geometry_msgs::msg::TwistWithCovariance>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<derived_object_msgs::msg::ObjectWithCovariance>
  : std::integral_constant<bool, has_bounded_size<derived_object_msgs::msg::SolidPrimitiveWithCovariance>::value && has_bounded_size<geometry_msgs::msg::AccelWithCovariance>::value && has_bounded_size<geometry_msgs::msg::Polygon>::value && has_bounded_size<geometry_msgs::msg::PoseWithCovariance>::value && has_bounded_size<geometry_msgs::msg::TwistWithCovariance>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<derived_object_msgs::msg::ObjectWithCovariance>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DERIVED_OBJECT_MSGS__MSG__DETAIL__OBJECT_WITH_COVARIANCE__TRAITS_HPP_
