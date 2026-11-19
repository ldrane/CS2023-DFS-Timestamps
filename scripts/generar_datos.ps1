$ErrorActionPreference = "Stop"
g++ -std=c++17 -O2 -Wall cpp\dfs_timestamps.cpp -o dfs_timestamps
New-Item -ItemType Directory -Force datos | Out-Null
.\dfs_timestamps datos\
