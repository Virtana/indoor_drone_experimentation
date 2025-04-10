#!/bin/bash

# Define the parent directories to display
PARENT_DIRS=("Custom_Datasets" "Euroc_Datasets")

# Define the destination directory
DEST_DIR="mav0"

# Check if the destination directory exists, create it if it doesn't
if [ ! -d "$DEST_DIR" ]; then
  mkdir -p "$DEST_DIR"
  echo "Created destination directory: $DEST_DIR"
fi

# Display the contents of the parent directories
echo "Available datasets:"
INDEX=1
declare -A SUBDIR_MAP  # To map selection numbers to subdirectory paths

for PARENT_DIR in "${PARENT_DIRS[@]}"; do
  if [ -d "$PARENT_DIR" ]; then
    echo "Contents of $PARENT_DIR:"
    SUBDIRS=("$PARENT_DIR"/*/)
    for SUBDIR in "${SUBDIRS[@]}"; do
      if [ -d "$SUBDIR" ]; then
        echo "  $INDEX. $(basename "$SUBDIR")"
        SUBDIR_MAP[$INDEX]="$SUBDIR"
        INDEX=$((INDEX+1))
      fi
    done
  else
    echo "Directory $PARENT_DIR does not exist."
  fi
done

# Check if any subdirectories were found
if [ ${#SUBDIR_MAP[@]} -eq 0 ]; then
  echo "No subdirectories found in the specified datasets."
  exit 1
fi

# Prompt the user to select a subdirectory
read -p "Enter the number of the subdirectory you want to copy: " SELECTION

# Validate the user's input
if [[ ! "$SELECTION" =~ ^[0-9]+$ ]] || [ -z "${SUBDIR_MAP[$SELECTION]}" ]; then
  echo "Invalid selection. Please enter a valid number from the list."
  exit 1
fi

# Get the selected subdirectory
SELECTED_SUBDIR="${SUBDIR_MAP[$SELECTION]}"
SELECTED_SUBDIR_NAME=$(basename "$SELECTED_SUBDIR")

#Clear contents of selected subdirectory before copying.
rm -r "$DEST_DIR/"

# Copy the selected subdirectory to the mav0 directory
cp -r "$SELECTED_SUBDIR/mav0/." "$DEST_DIR/"

# Check if the copy was successful
if [ $? -eq 0 ]; then
  echo "Contents of subdirectory '$SELECTED_SUBDIR_NAME/mav0' has been copied to '$DEST_DIR'."
  echo "Current dataset: $SELECTED_SUBDIR" > datasetname.txt 
else
  echo "Error: Failed to copy subdirectory '$SELECTED_SUBDIR_NAME'."
fi