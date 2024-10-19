#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
	echo "Usage: $0 <number_of_season> <path>"
	exit 1
fi

num_seasons=$1
target_path=$2

if [ ! -d "$target_path" ]; then
	echo "The specified path does not exist: $target_path"
	exit 1
fi

for (( i=1; i <= num_seasons; i++))
do
	mkdir "$target_path/Season $i"
	echo "Created directory: $target_path/Season $i"
done