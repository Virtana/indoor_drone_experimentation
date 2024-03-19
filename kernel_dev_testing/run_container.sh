mkdir -p ./kernel
mkdir -p ./kernel/build

docker run -it \
--mount type=bind,source=./kernel,target=/compulab_kernel \
cl_kernel
