#!/bin/bash
# This script should be placed and executed in the scripts directory.

FILE="../params/EurocMono/BackendParams.yaml"
# Update the linearizationMode parameter to 1
sed -i 's/^\(linearizationMode:\s*\).*/\11/' "$FILE"
echo "Updated linearizationMode in $FILE"

FILE="../params/EurocMono/FrontendParams.yaml"
# Update the maxFeatureAge parameter to 25
sed -i 's/^\(maxFeatureAge:\s*\).*/\125/' "$FILE"
sed -i 's/^\(feature_detector_type:\s*\).*/\10/' "$FILE"
# Update the maxFeaturesPerFrame parameter to 300
sed -i 's/^\(maxFeaturesPerFrame:\s*\).*/\1300/' "$FILE"
sed -i 's/^\(min_intra_keyframe_time:\s*\).*/\10.2/' "$FILE"
sed -i 's/^\(max_intra_keyframe_time:\s*\).*/\10.2/' "$FILE"
echo "Updated maxFeatureAge, feature_detector_type, maxFeaturesPerFrame, min_intra_keyframe_time and max_intra_keyframe_time in $FILE"

FILE="./stereoVIOEuroc.bash"
sed -i "s|^\(DATASET_PATH=\).*|\1\"/data/datasets/Euroc\"|" "$FILE"
sed -i "s|^\(LOG_OUTPUT=\).*|\11|" "$FILE"
sed -i "s|^\(PARAMS_PATH=\).*|\1"../params/EurocMono"|" "$FILE"
echo "Updated DATASET_PATH and LOG_OUTPUT params in $FILE"