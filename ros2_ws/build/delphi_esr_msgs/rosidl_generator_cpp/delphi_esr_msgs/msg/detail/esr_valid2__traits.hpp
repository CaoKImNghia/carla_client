// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from delphi_esr_msgs:msg/EsrValid2.idl
// generated code does not contain a copyright notice

#ifndef DELPHI_ESR_MSGS__MSG__DETAIL__ESR_VALID2__TRAITS_HPP_
#define DELPHI_ESR_MSGS__MSG__DETAIL__ESR_VALID2__TRAITS_HPP_

#include "delphi_esr_msgs/msg/detail/esr_valid2__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<delphi_esr_msgs::msg::EsrValid2>()
{
  return "delphi_esr_msgs::msg::EsrValid2";
}

template<>
inline const char * name<delphi_esr_msgs::msg::EsrValid2>()
{
  return "delphi_esr_msgs/msg/EsrValid2";
}

template<>
struct has_fixed_size<delphi_esr_msgs::msg::EsrValid2>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<delphi_esr_msgs::msg::EsrValid2>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<delphi_esr_msgs::msg::EsrValid2>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DELPHI_ESR_MSGS__MSG__DETAIL__ESR_VALID2__TRAITS_HPP_
