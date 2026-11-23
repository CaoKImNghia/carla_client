// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ibeo_msgs:msg/ScanData2208.idl
// generated code does not contain a copyright notice

#ifndef IBEO_MSGS__MSG__DETAIL__SCAN_DATA2208__TRAITS_HPP_
#define IBEO_MSGS__MSG__DETAIL__SCAN_DATA2208__TRAITS_HPP_

#include "ibeo_msgs/msg/detail/scan_data2208__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'ibeo_header'
#include "ibeo_msgs/msg/detail/ibeo_data_header__traits.hpp"
// Member 'scan_start_time'
// Member 'scan_end_time'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<ibeo_msgs::msg::ScanData2208>()
{
  return "ibeo_msgs::msg::ScanData2208";
}

template<>
inline const char * name<ibeo_msgs::msg::ScanData2208>()
{
  return "ibeo_msgs/msg/ScanData2208";
}

template<>
struct has_fixed_size<ibeo_msgs::msg::ScanData2208>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<ibeo_msgs::msg::ScanData2208>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<ibeo_msgs::msg::ScanData2208>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // IBEO_MSGS__MSG__DETAIL__SCAN_DATA2208__TRAITS_HPP_
