// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from derived_object_msgs:msg/ObjectArray.idl
// generated code does not contain a copyright notice

#ifndef DERIVED_OBJECT_MSGS__MSG__DETAIL__OBJECT_ARRAY__TRAITS_HPP_
#define DERIVED_OBJECT_MSGS__MSG__DETAIL__OBJECT_ARRAY__TRAITS_HPP_

#include "derived_object_msgs/msg/detail/object_array__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<derived_object_msgs::msg::ObjectArray>()
{
  return "derived_object_msgs::msg::ObjectArray";
}

template<>
inline const char * name<derived_object_msgs::msg::ObjectArray>()
{
  return "derived_object_msgs/msg/ObjectArray";
}

template<>
struct has_fixed_size<derived_object_msgs::msg::ObjectArray>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<derived_object_msgs::msg::ObjectArray>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<derived_object_msgs::msg::ObjectArray>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DERIVED_OBJECT_MSGS__MSG__DETAIL__OBJECT_ARRAY__TRAITS_HPP_
