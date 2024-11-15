#!/bin/bash

# Check if the correct number of arguments is provided
if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <sXX> <sYY> <target_folder>"
    exit 1
fi

# Assign input arguments to variables
OLD_SUBSTRING="$1"
NEW_SUBSTRING="$2"
TARGET_FOLDER="$3"

# Convert Windows paths to Unix-style paths if necessary
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    TARGET_FOLDER=$(cygpath "$TARGET_FOLDER")
fi

# Check if the target folder exists
if [[ ! -d "$TARGET_FOLDER" ]]; then
    echo "Error: Target folder '$TARGET_FOLDER' does not exist."
    exit 1
fi

# Iterate over all files in the target folder
for file in "$TARGET_FOLDER"/*; do
    # Get the base name of the file
    base_name=$(basename "$file")
    
	echo "$base_name"
	# Generate the new file name by replacing the old substring
	new_base_name="${base_name//$OLD_SUBSTRING/$NEW_SUBSTRING}"
	new_file="$TARGET_FOLDER/$new_base_name"
	
	# Rename the file
	mv "$file" "$new_file"
	echo "Renamed: $file -> $new_file"
done

echo "Renaming complete."
