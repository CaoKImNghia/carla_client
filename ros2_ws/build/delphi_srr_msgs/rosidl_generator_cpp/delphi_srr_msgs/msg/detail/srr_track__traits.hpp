// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from delphi_srr_msgs:msg/SrrTrack.idl
// generated code does not contain a copyright notice

#ifndef DELPHI_SRR_MSGS__MSG__DETAIL__SRR_TRACK__TRAITS_HPP_
#define DELPHI_SRR_MSGS__MSG__DETAIL__SRR_TRACK__TRAITS_HPP_

#include "delphi_srr_msgs/msg/detail/srr_track__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<delphi_srr_msgs::msg::SrrTrack>()
{
  return "delphi_srr_msgs::msg::SrrTrack";
}

template<>
inline const char * name<delphi_srr_msgs::msg::SrrTrack>()
{
  return "delphi_srr_msgs/msg/SrrTrack";
}

template<>
struct has_fixed_size<delphi_srr_msgs::msg::SrrTrack>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<delphi_srr_msgs::msg::SrrTrack>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<delphi_srr_msgs::msg::SrrTrack>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DELPHI_SRR_MSGS__MSG__DETAIL__SRR_TRACK__TRAITS_HPP_
