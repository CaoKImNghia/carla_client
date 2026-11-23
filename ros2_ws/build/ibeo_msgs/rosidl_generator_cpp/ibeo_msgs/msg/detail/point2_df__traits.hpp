// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ibeo_msgs:msg/Point2Df.idl
// generated code does not contain a copyright notice

#ifndef IBEO_MSGS__MSG__DETAIL__POINT2_DF__TRAITS_HPP_
#define IBEO_MSGS__MSG__DETAIL__POINT2_DF__TRAITS_HPP_

#include "ibeo_msgs/msg/detail/point2_df__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<ibeo_msgs::msg::Point2Df>()
{
  return "ibeo_msgs::msg::Point2Df";
}

template<>
inline const char * name<ibeo_msgs::msg::Point2Df>()
{
  return "ibeo_msgs/msg/Point2Df";
}

template<>
struct has_fixed_size<ibeo_msgs::msg::Point2Df>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<ibeo_msgs::msg::Point2Df>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<ibeo_msgs::msg::Point2Df>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // IBEO_MSGS__MSG__DETAIL__POINT2_DF__TRAITS_HPP_
