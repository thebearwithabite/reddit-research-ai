#!/bin/bash

# This script runs the Reddit posting automation.
# Usage: ./run_reddit_post.sh <schema_file> [--publish]

SCHEMA_FILE=$1
PUBLISH_FLAG="false"

if [ "$2" == "--publish" ]; then
    PUBLISH_FLAG="true"
fi

if [ -z "$SCHEMA_FILE" ]; then
    echo "Usage: ./run_reddit_post.sh <schema_file> [--publish]"
    exit 1
fi

# Ensure Python dependencies are installed
pip install -r requirements.txt

# Run the Python automation script
python3 automation_pipeline.py "$SCHEMA_FILE" "$PUBLISH_FLAG"
