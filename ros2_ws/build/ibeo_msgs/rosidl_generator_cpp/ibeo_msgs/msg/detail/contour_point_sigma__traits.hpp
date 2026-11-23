// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ibeo_msgs:msg/ContourPointSigma.idl
// generated code does not contain a copyright notice

#ifndef IBEO_MSGS__MSG__DETAIL__CONTOUR_POINT_SIGMA__TRAITS_HPP_
#define IBEO_MSGS__MSG__DETAIL__CONTOUR_POINT_SIGMA__TRAITS_HPP_

#include "ibeo_msgs/msg/detail/contour_point_sigma__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<ibeo_msgs::msg::ContourPointSigma>()
{
  return "ibeo_msgs::msg::ContourPointSigma";
}

template<>
inline const char * name<ibeo_msgs::msg::ContourPointSigma>()
{
  return "ibeo_msgs/msg/ContourPointSigma";
}

template<>
struct has_fixed_size<ibeo_msgs::msg::ContourPointSigma>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<ibeo_msgs::msg::ContourPointSigma>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<ibeo_msgs::msg::ContourPointSigma>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // IBEO_MSGS__MSG__DETAIL__CONTOUR_POINT_SIGMA__TRAITS_HPP_
