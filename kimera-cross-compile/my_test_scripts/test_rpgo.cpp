#include <stdlib.h>
// #include <memory>
// #include <string>

// #include <gtsam/geometry/Pose2.h>
// #include <gtsam/geometry/Pose3.h>
// #include <gtsam/slam/dataset.h>

#include "KimeraRPGO/RobustSolver.h"
#include "KimeraRPGO/SolverParams.h"
#include "KimeraRPGO/Logger.h"
#include "KimeraRPGO/utils/GeometryUtils.h"
#include "KimeraRPGO/utils/TypeUtils.h"

using namespace KimeraRPGO;

int main() {
    // Set up
    // set up KimeraRPGO solver
    RobustSolverParams params;
    params.setPcm3DParams(0.0, 10.0, Verbosity::VERBOSE);
    std::cout << "Reached end of script" << std::endl;
}