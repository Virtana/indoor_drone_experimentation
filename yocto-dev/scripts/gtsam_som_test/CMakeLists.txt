cmake_minimum_required(VERSION 3.10.0)
project(RpgoTest)

# Linking boost
find_package(Boost 1.78.0 REQUIRED system filesystem serialization REQUIRED)
include_directories(${Boost_INCLUDE_DIR})

# Linking Eigen
find_package(Eigen3 REQUIRED)
include_directories(SYSTEM ${EIGEN3_INCLUDE_DIRS})

# Linking gtsam
find_package(GTSAM REQUIRED)

if(Boost_FOUND AND GTSAM_FOUND)
    message("Found boost AND gtsam")
    include_directories(${Boost_INCLUDE_DIR} ${GTSAM_INCLUDE_DIR})

    # Add your executable and link against all Boost and GTSAM libraries
    add_executable(gtsam_test test_gtsam.cpp)
    
    target_link_libraries(
        gtsam_test PRIVATE ${Boost_LIBRARIES} gtsam ${GTSAM_LIBRARIES}
    )
else()
    message(FATAL_ERROR "Boost or GTSAM not found. Please install Boost and GTSAM or adjust the CMake configuration.")
endif()

