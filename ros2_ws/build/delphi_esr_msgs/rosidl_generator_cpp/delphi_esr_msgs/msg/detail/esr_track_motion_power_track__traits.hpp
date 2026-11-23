// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from delphi_esr_msgs:msg/EsrTrackMotionPowerTrack.idl
// generated code does not contain a copyright notice

#ifndef DELPHI_ESR_MSGS__MSG__DETAIL__ESR_TRACK_MOTION_POWER_TRACK__TRAITS_HPP_
#define DELPHI_ESR_MSGS__MSG__DETAIL__ESR_TRACK_MOTION_POWER_TRACK__TRAITS_HPP_

#include "delphi_esr_msgs/msg/detail/esr_track_motion_power_track__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<delphi_esr_msgs::msg::EsrTrackMotionPowerTrack>()
{
  return "delphi_esr_msgs::msg::EsrTrackMotionPowerTrack";
}

template<>
inline const char * name<delphi_esr_msgs::msg::EsrTrackMotionPowerTrack>()
{
  return "delphi_esr_msgs/msg/EsrTrackMotionPowerTrack";
}

template<>
struct has_fixed_size<delphi_esr_msgs::msg::EsrTrackMotionPowerTrack>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<delphi_esr_msgs::msg::EsrTrackMotionPowerTrack>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<delphi_esr_msgs::msg::EsrTrackMotionPowerTrack>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DELPHI_ESR_MSGS__MSG__DETAIL__ESR_TRACK_MOTION_POWER_TRACK__TRAITS_HPP_
