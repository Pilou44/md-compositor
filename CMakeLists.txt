cmake_minimum_required(VERSION 3.16)
project(md_compositor LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

add_executable(md_compositor
  src/main.cpp
)

target_include_directories(md_compositor PRIVATE
  ${CMAKE_SOURCE_DIR}/third_party
)

target_compile_options(md_compositor PRIVATE -Wall -Wextra)
