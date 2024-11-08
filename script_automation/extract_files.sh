'''
to extract relevant motion capture files within a subject directory

target files including:
"*.trc" "*.c3d" "*.mat" "*.osim"

run the following:
chmod +x extract_files.sh
./extract_files.sh /absolute_path_to_subject_folder
'''

#!/bin/bash

# Define the top-level directory
TOP_DIR="$1"  # Pass the directory path as an argument, e.g., ./script.sh /path/to/td_dimitrov/P02
SAVE_DIR="dk_extracted_files"

# Check if the directory exists
if [ ! -d "$TOP_DIR" ]; then
  echo "The specified directory does not exist: $TOP_DIR"
  exit 1
fi

# Create the save directory within the top-level directory
SAVE_PATH="$TOP_DIR/$SAVE_DIR"
mkdir -p "$SAVE_PATH"

# Define file extensions to search for
EXTENSIONS=("*.trc" "*.c3d" "*.mat" "*.osim")

# Find and copy files
for ext in "${EXTENSIONS[@]}"; do
  find "$TOP_DIR" -type f -name "$ext" -exec cp {} "$SAVE_PATH" \;
done

echo "Files with specified extensions have been copied to $SAVE_PATH"
