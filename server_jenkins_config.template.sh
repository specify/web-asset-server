#!/bin/bash
image_password="test_password"
metadata_requirements_path="metadata_tools/requirements.txt"
python_path=$(pwd)3
lockfile="/tmp/jenkins_script.lock"

cleanup() {
    rm -f "$lockfile"
    echo "Lockfile removed."
}