// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ibeo_msgs:msg/ScannerInfo2205.idl
// generated code does not contain a copyright notice

#ifndef IBEO_MSGS__MSG__DETAIL__SCANNER_INFO2205__TRAITS_HPP_
#define IBEO_MSGS__MSG__DETAIL__SCANNER_INFO2205__TRAITS_HPP_

#include "ibeo_msgs/msg/detail/scanner_info2205__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'scan_start_time'
// Member 'scan_end_time'
// Member 'scan_start_time_from_device'
// Member 'scan_end_time_from_device'
#include "builtin_interfaces/msg/detail/time__traits.hpp"
// Member 'mounting_position'
#include "ibeo_msgs/msg/detail/mounting_position_f__traits.hpp"
// Member 'resolutions'
#include "ibeo_msgs/msg/detail/resolution_info__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<ibeo_msgs::msg::ScannerInfo2205>()
{
  return "ibeo_msgs::msg::ScannerInfo2205";
}

template<>
inline const char * name<ibeo_msgs::msg::ScannerInfo2205>()
{
  return "ibeo_msgs/msg/ScannerInfo2205";
}

template<>
struct has_fixed_size<ibeo_msgs::msg::ScannerInfo2205>
  : std::integral_constant<bool, has_fixed_size<builtin_interfaces::msg::Time>::value && has_fixed_size<ibeo_msgs::msg::MountingPositionF>::value && has_fixed_size<ibeo_msgs::msg::ResolutionInfo>::value> {};

template<>
struct has_bounded_size<ibeo_msgs::msg::ScannerInfo2205>
  : std::integral_constant<bool, has_bounded_size<builtin_interfaces::msg::Time>::value && has_bounded_size<ibeo_msgs::msg::MountingPositionF>::value && has_bounded_size<ibeo_msgs::msg::ResolutionInfo>::value> {};

template<>
struct is_message<ibeo_msgs::msg::ScannerInfo2205>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // IBEO_MSGS__MSG__DETAIL__SCANNER_INFO2205__TRAITS_HPP_
