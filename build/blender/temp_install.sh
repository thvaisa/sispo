#!/bin/bash

echo "Installing blender as a python module start"

# Creating blender directory
cd software
[[ -d blender ]] || mkdir blender
cd blender

# Get blender repo
git clone https://git.blender.org/blender.git
cd blender
git submodule update --init --recursive
git submodule foreach git checkout master
git submodule foreach pull --rebase origin master

# Dependencies
#chmod +x build_files/build_environment/install_deps.sh
#./build_files/build_environment/install_deps.sh --with-all --no-confirm

# Update files
make update

# Configure and install blender bpy
cd ..
[[ -d build_blender_bpy ]] || mkdir build_blender_bpy
cd build_blender_bpy
cmake \
	-C ../blender/build_files/cmake/config/bpy_module.cmake \
	-S ../blender \
    -DWITH_IMAGE_OPENEXR=ON \
    -DPYTHON_SITE_PACKAGES=/home/travis/miniconda/envs/sispo/lib/python3.7/site-packages
    #-DPYTHON_LIBRARY=/home/travis/miniconda/envs/sispo/lib/python3.7/config-3.7m-x86_64-linux-gnu/libpython3.7m.so \
    #-DPYTHON_LIBPATH=/home/travis/miniconda/envs/sispo/lib \
    #-DPYTHON_INCLUDE_DIR=/home/travis/miniconda/envs/sispo/include \
    #-DPYTHON_INCLUDE_CONFIG_DIR=/home/travis/miniconda/envs/sispo/lib/python3.7/config-3.7m-x86_64-linux-gnu