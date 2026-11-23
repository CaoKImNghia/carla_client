// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from delphi_mrr_msgs:msg/VehicleStateMsg3.idl
// generated code does not contain a copyright notice

#ifndef DELPHI_MRR_MSGS__MSG__DETAIL__VEHICLE_STATE_MSG3__TRAITS_HPP_
#define DELPHI_MRR_MSGS__MSG__DETAIL__VEHICLE_STATE_MSG3__TRAITS_HPP_

#include "delphi_mrr_msgs/msg/detail/vehicle_state_msg3__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<delphi_mrr_msgs::msg::VehicleStateMsg3>()
{
  return "delphi_mrr_msgs::msg::VehicleStateMsg3";
}

template<>
inline const char * name<delphi_mrr_msgs::msg::VehicleStateMsg3>()
{
  return "delphi_mrr_msgs/msg/VehicleStateMsg3";
}

template<>
struct has_fixed_size<delphi_mrr_msgs::msg::VehicleStateMsg3>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<delphi_mrr_msgs::msg::VehicleStateMsg3>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<delphi_mrr_msgs::msg::VehicleStateMsg3>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DELPHI_MRR_MSGS__MSG__DETAIL__VEHICLE_STATE_MSG3__TRAITS_HPP_
