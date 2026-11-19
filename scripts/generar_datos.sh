#!/usr/bin/env bash
set -e
g++ -std=c++17 -O2 -Wall cpp/dfs_timestamps.cpp -o dfs_timestamps
mkdir -p datos
./dfs_timestamps datos/
