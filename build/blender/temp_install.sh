#!/bin/bash
#if [[ -f /home/travis/build/YgabrielsY/sispo/software/blender/build_linux_bpy/bin/bpy.so ]]; then
#    echo "Using cached bpy"
#    cd software/blender/build_linux_bpy
#    make install
#else
echo "Installing blender as a python module start"

# Creating blender directory
cd software
[[ -d blender ]] || mkdir blender  
cd blender

# Get blender repo
git clone https://git.blender.org/blender.git
cd blender
#git submodule update --init --recursive
#git submodule foreach git checkout master
#git submodule foreach pull --rebase origin master

# Dependencies
chmod +x build_files/build_environment/install_deps.sh
./build_files/build_environment/install_deps.sh --with-all --no-confirm --skip-oidn --skip-osd

# Update files
make update

# Bpy
BUILD_CMAKE_ARGS="-DPYTHON_SITE_PACKAGES:FILEPATH=/home/travis/miniconda/envs/sispo/lib/python3.7/site-packages"
export BUILD_CMAKE_ARGS
make bpy
#fi