// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from derived_object_msgs:msg/Lane.idl
// generated code does not contain a copyright notice

#ifndef DERIVED_OBJECT_MSGS__MSG__DETAIL__LANE__TRAITS_HPP_
#define DERIVED_OBJECT_MSGS__MSG__DETAIL__LANE__TRAITS_HPP_

#include "derived_object_msgs/msg/detail/lane__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<derived_object_msgs::msg::Lane>()
{
  return "derived_object_msgs::msg::Lane";
}

template<>
inline const char * name<derived_object_msgs::msg::Lane>()
{
  return "derived_object_msgs/msg/Lane";
}

template<>
struct has_fixed_size<derived_object_msgs::msg::Lane>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<derived_object_msgs::msg::Lane>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<derived_object_msgs::msg::Lane>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DERIVED_OBJECT_MSGS__MSG__DETAIL__LANE__TRAITS_HPP_
