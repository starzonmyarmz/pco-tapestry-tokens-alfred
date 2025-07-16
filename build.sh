#!/bin/bash

# Build script for Tapestry Tokens Alfred workflow
# This script deletes the current alfredworkflow and regenerates a new one ignoring gitignore files
# Usage: ./build.sh [major|minor|patch]

set -e

WORKFLOW_NAME="tapestry-tokens.alfredworkflow"
PLIST_FILE="info.plist"

# Check if version bump argument is provided
if [ $# -eq 0 ]; then
    echo "Error: Version bump required. Usage: ./build.sh [major|minor|patch]"
    exit 1
fi

VERSION_BUMP=$1

# Validate version bump argument
if [[ "$VERSION_BUMP" != "major" && "$VERSION_BUMP" != "minor" && "$VERSION_BUMP" != "patch" ]]; then
    echo "Error: Invalid version bump. Must be 'major', 'minor', or 'patch'"
    exit 1
fi

# Extract current version from info.plist
CURRENT_VERSION=$(grep -A1 '<key>version</key>' "$PLIST_FILE" | grep '<string>' | sed 's/.*<string>\(.*\)<\/string>.*/\1/')

if [ -z "$CURRENT_VERSION" ]; then
    echo "Error: Could not find version in $PLIST_FILE"
    exit 1
fi

echo "Current version: $CURRENT_VERSION"

# Parse version components
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Bump version based on argument
case "$VERSION_BUMP" in
    "major")
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    "minor")
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    "patch")
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "New version: $NEW_VERSION"

# Update version in info.plist
sed -i '' "s/<string>$CURRENT_VERSION<\/string>/<string>$NEW_VERSION<\/string>/" "$PLIST_FILE"

echo "Building $WORKFLOW_NAME with version $NEW_VERSION..."

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

echo "Successfully built $WORKFLOW_NAME version $NEW_VERSION"