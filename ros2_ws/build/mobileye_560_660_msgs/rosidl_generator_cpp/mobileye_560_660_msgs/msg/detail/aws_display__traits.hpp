// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from mobileye_560_660_msgs:msg/AwsDisplay.idl
// generated code does not contain a copyright notice

#ifndef MOBILEYE_560_660_MSGS__MSG__DETAIL__AWS_DISPLAY__TRAITS_HPP_
#define MOBILEYE_560_660_MSGS__MSG__DETAIL__AWS_DISPLAY__TRAITS_HPP_

#include "mobileye_560_660_msgs/msg/detail/aws_display__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<mobileye_560_660_msgs::msg::AwsDisplay>()
{
  return "mobileye_560_660_msgs::msg::AwsDisplay";
}

template<>
inline const char * name<mobileye_560_660_msgs::msg::AwsDisplay>()
{
  return "mobileye_560_660_msgs/msg/AwsDisplay";
}

template<>
struct has_fixed_size<mobileye_560_660_msgs::msg::AwsDisplay>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<mobileye_560_660_msgs::msg::AwsDisplay>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<mobileye_560_660_msgs::msg::AwsDisplay>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MOBILEYE_560_660_MSGS__MSG__DETAIL__AWS_DISPLAY__TRAITS_HPP_
