#!/bin/bash
image_password="test_password"
metadata_requirements_path="metadata_tools/requirements.txt"
python_path=$(pwd)
lockfile="/tmp/jenkins_script.lock"

cleanup() {
    rm -f "$lockfile"
    echo "Lockfile removed."
    rm -r venv
    # cleanup tmp pip files
    rm -rf /tmp/pip-*
}


replace_https_with_http() {
    local file="$1"
    if [[ -f "$file" ]]; then
        # Replace 'https' with 'http' in place
        sed -i.bak 's/https/http/g' "$file"
        rm -f "${file}.bak"
        echo "Replaced 'https' with 'http' in $file."
    else
        echo "File $file not found."
    fi
}

convert_to_http() {
  files=(
      "tests/test_server.py"
      "views/web_asset_store.xml"
  )
  # Loop through each file and run the replacement function
  for file in "${files[@]}"; do
      replace_https_with_http "$file"
  done
}