#!/bin/bash
echo "Installing blender as a python module start"

# Creating blender directory
cd software
[[ -d blender ]] || mkdir blender  
cd blender

# Get blender repo
if [[ -d software/blender ]]; then
    echo "Blender folder exists, no cloning"
else
    git clone https://git.blender.org/blender.git
fi
cd blender
git checkout tags/v2.81

# Dependencies
chmod +x build_files/build_environment/install_deps.sh
./build_files/build_environment/install_deps.sh --with-all --no-confirm

# Update files
make update

# Bpy
BUILD_CMAKE_ARGS="-DPYTHON_SITE_PACKAGES:FILEPATH=/home/travis/miniconda/envs/sispo/lib/python3.7/site-packages"
export BUILD_CMAKE_ARGS
make bpy