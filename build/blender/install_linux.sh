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

# Update files and use version 2.81
make update
git checkout tags/v2.81
make update

# Dependencies
chmod +x build_files/build_environment/install_deps.sh
./build_files/build_environment/install_deps.sh --source ../lib/src --install ../lib --with-all --no-confirm

# Bpy
BUILD_CMAKE_ARGS="-DPYTHON_SITE_PACKAGES:FILEPATH=/home/travis/miniconda/envs/sispo/lib/python3.7/site-packages"
export BUILD_CMAKE_ARGS
make bpy

echo "Installing blender as a python module done"