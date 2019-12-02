cmake_minimum_required(VERSION 3.1)
project(QVec)

find_package(LLVM REQUIRED CONFIG)

set(LLVM_INCLUDE_DIRS ../llvm/include ../build/include/)
set(LLVM_LIBRARY_DIRS ../build/Release+Asserts/lib/)

add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})
link_directories(${LLVM_LIBRARY_DIRS})

add_subdirectory(src)  # Use your pass name here.