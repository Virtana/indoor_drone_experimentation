cmake_minimum_required(VERSION 3.10.0)
project(RpgoTest)

# Linking boost
# find_package(Boost COMPONENTS ALL REQUIRED)
# find_package(Boost 1.84.0 REQUIRED system filesystem serialization REQUIRED)
find_package(Boost 1.65.0 REQUIRED system filesystem serialization REQUIRED)
include_directories(${Boost_INCLUDE_DIR})

# Adding path to Eigen to includes
include_directories(/usr/local/include/gtsam/3rdparty/)
include_directories(/usr/local/include/gtsam/3rdparty/Eigen)

# Linking gtsam
find_package(GTSAM REQUIRED)

# libkimera-rpgo
find_package(KimeraRPGO)

if(Boost_FOUND AND GTSAM_FOUND)
    message("Found boost AND gtsam")
    include_directories(${Boost_INCLUDE_DIR} ${GTSAM_INCLUDE_DIR})

    # Add your executable and link against all Boost and GTSAM libraries
    add_executable(gpgo_test test_rpgo.cpp)
    
    # target_link_libraries(
    #     gtsam INTERFACE ${Boost_LIBRARIES}
    # )

    target_link_libraries(
        # gtsam_test PRIVATE ${Boost_LIBRARIES} gtsam #${GTSAM_LIBRARIES}
        gpgo_test PRIVATE ${Boost_LIBRARIES} metis-gtsam gtsam gtsam_unstable KimeraRPGO
    )
else()
    message(FATAL_ERROR "Boost or GTSAM not found. Please install Boost and GTSAM or adjust the CMake configuration.")
endif()
