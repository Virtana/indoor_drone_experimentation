xhost +local:root
docker run --rm -it --network=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v /home/shiva/Datasets:/data/datasets/Euroc \
    kimera_vio /bin/bash
