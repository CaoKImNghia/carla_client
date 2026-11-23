// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from derived_object_msgs:msg/SolidPrimitiveWithCovariance.idl
// generated code does not contain a copyright notice

#ifndef DERIVED_OBJECT_MSGS__MSG__DETAIL__SOLID_PRIMITIVE_WITH_COVARIANCE__TRAITS_HPP_
#define DERIVED_OBJECT_MSGS__MSG__DETAIL__SOLID_PRIMITIVE_WITH_COVARIANCE__TRAITS_HPP_

#include "derived_object_msgs/msg/detail/solid_primitive_with_covariance__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<derived_object_msgs::msg::SolidPrimitiveWithCovariance>()
{
  return "derived_object_msgs::msg::SolidPrimitiveWithCovariance";
}

template<>
inline const char * name<derived_object_msgs::msg::SolidPrimitiveWithCovariance>()
{
  return "derived_object_msgs/msg/SolidPrimitiveWithCovariance";
}

template<>
struct has_fixed_size<derived_object_msgs::msg::SolidPrimitiveWithCovariance>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<derived_object_msgs::msg::SolidPrimitiveWithCovariance>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<derived_object_msgs::msg::SolidPrimitiveWithCovariance>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DERIVED_OBJECT_MSGS__MSG__DETAIL__SOLID_PRIMITIVE_WITH_COVARIANCE__TRAITS_HPP_
