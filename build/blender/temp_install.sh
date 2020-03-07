#!/bin/bash

echo "Installing blender as a python module start"

# Creating blender directory
cd ~/
[[ -d blender ]] || mkdir blender
cd blender

# Get blender repo
git clone https://git.blender.org/blender.git
cd blender
git submodule update --init --recursive
git submodule foreach git checkout master
git submodule foreach pull --rebase origin master

# Dependencies
./blender/build_files/build_environment/install_deps.sh

# Update files
make update

# Build
make bpy

