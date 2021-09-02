#!/bin/bash

dump="$1"
index="$2"
stat="$3"

# Create folders for index & stat file (if doesn't exists)
mkdir -p "$index"
mkdir -p "$(dirname "$stat")"

python3 indexer.py "$dump" "$index" "$stat"