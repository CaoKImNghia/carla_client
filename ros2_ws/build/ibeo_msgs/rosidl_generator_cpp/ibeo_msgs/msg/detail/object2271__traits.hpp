// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ibeo_msgs:msg/Object2271.idl
// generated code does not contain a copyright notice

#ifndef IBEO_MSGS__MSG__DETAIL__OBJECT2271__TRAITS_HPP_
#define IBEO_MSGS__MSG__DETAIL__OBJECT2271__TRAITS_HPP_

#include "ibeo_msgs/msg/detail/object2271__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'tracked_properties'
#include "ibeo_msgs/msg/detail/tracked_properties__traits.hpp"
// Member 'untracked_properties'
#include "ibeo_msgs/msg/detail/untracked_properties__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<ibeo_msgs::msg::Object2271>()
{
  return "ibeo_msgs::msg::Object2271";
}

template<>
inline const char * name<ibeo_msgs::msg::Object2271>()
{
  return "ibeo_msgs/msg/Object2271";
}

template<>
struct has_fixed_size<ibeo_msgs::msg::Object2271>
  : std::integral_constant<bool, has_fixed_size<ibeo_msgs::msg::TrackedProperties>::value && has_fixed_size<ibeo_msgs::msg::UntrackedProperties>::value> {};

template<>
struct has_bounded_size<ibeo_msgs::msg::Object2271>
  : std::integral_constant<bool, has_bounded_size<ibeo_msgs::msg::TrackedProperties>::value && has_bounded_size<ibeo_msgs::msg::UntrackedProperties>::value> {};

template<>
struct is_message<ibeo_msgs::msg::Object2271>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // IBEO_MSGS__MSG__DETAIL__OBJECT2271__TRAITS_HPP_
