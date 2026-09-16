cmake_minimum_required(VERSION 3.16)
project(md_compositor LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

# --- La lib : header-only, exposée pour être consommée ailleurs ---
add_library(md_compositor INTERFACE)
target_include_directories(md_compositor INTERFACE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# --- Le banc de test : consomme la lib ---
add_executable(shapes_test
  tests/shapes/main.cpp
)

target_include_directories(shapes_test PRIVATE
  ${CMAKE_SOURCE_DIR}/third_party
)

target_link_libraries(shapes_test PRIVATE md_compositor)

target_compile_options(shapes_test PRIVATE -Wall -Wextra)
