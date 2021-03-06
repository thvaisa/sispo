#!/bin/bash

echo "Download ucac4 star catalogue start"

# Creating dir
cd ../..
[[ -d data ]] || mkdir data
cd data

[[ -d ucac4 ]] || mkdir ucac4
cd ucac4

# Download data
wget -r --no-parent -P . http://casdc.china-vo.org/mirror/UCAC/UCAC4/u4b/ &
wget -r --no-parent -P . http://casdc.china-vo.org/mirror/UCAC/UCAC4/u4i/
wait

# Moving files
[[ -d u4b ]] || mkdir u4b
[[ -d u4i ]] || mkdir u4i

mv casdc.china-vo.org/mirror/UCAC/UCAC4/u4b/* u4b
mv casdc.china-vo.org/mirror/UCAC/UCAC4/u4i/* u4i

rm -r casdc.china-vo.org/

echo "Download ucac4 star catalogue done"
