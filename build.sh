#!/bin/bash

# Build script for Tapestry Tokens Alfred workflow
# This script deletes the current alfredworkflow and regenerates a new one ignoring gitignore files

set -e

WORKFLOW_NAME="tapestry-tokens.alfredworkflow"

echo "Building $WORKFLOW_NAME..."

# Remove existing workflow file if it exists
if [ -f "$WORKFLOW_NAME" ]; then
    echo "Removing existing $WORKFLOW_NAME"
    rm "$WORKFLOW_NAME"
fi

# Create new workflow file, excluding gitignore patterns
echo "Creating new $WORKFLOW_NAME"
zip -r "$WORKFLOW_NAME" . \
    -x ".git/*" \
    -x ".claude/*" \
    -x ".last_update_check" \
    -x ".commit_hash" \
    -x "*.bak" \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x "*.pyo" \
    -x "*.pyd" \
    -x ".DS_Store" \
    -x "*.alfredworkflow" \
    -x ".gitignore" \
    -x "build.sh"

echo "Successfully built $WORKFLOW_NAME"