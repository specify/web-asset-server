#!/bin/bash
image_password="test_password"
metadata_requirements_path="metadata_tools/requirements.txt"
python_path=$(pwd)
lockfile="/tmp/$(basename "$0").lock"


# Function to remove the lockfile
cleanup() {
    rm -f "$lockfile"
    echo "Lockfile removed."
}

# cleanup lockfile on exit
trap cleanup EXIT

# checking lock
exec 200>$lockfile
flock -n 200 || { echo "Another instance of the script is already running. Exiting."; exit 1; }

unset PYTHONPATH

export PYTHONPATH=$python_path:$PYTHONPATH

echo $PYTHONPATH

rm -r venv

sleep 5

python3 -m venv venv

source venv/bin/activate

# Print Python version
echo "Python version:"
python --version

# Upgrade pip and install requirements

pip install --upgrade pip

git submodule update --init --remote --force

# waiting for submodule to populate
timeout=300
interval=2
elapsed=0

while [ ! -f ${metadata_requirements_path} ]; do
  if [ $elapsed -ge $timeout ]; then
    echo "Timeout reached: ${metadata_requirements_path} not found"
    exit 1
  fi
  echo "Waiting for ${metadata_requirements_path} to exist..."
  sleep $interval
  elapsed=$((elapsed + interval))
done

echo "${metadata_requirements_path} found"

pip install -r requirements.txt

pip install -r metadata_tools/requirements.txt

docker exec -i mysql-images mysql -u root -p"$image_password" -e "CREATE DATABASE IF NOT EXISTS images;"

docker exec -i mysql-images mysql -u root -p"$image_password" images < images_ddl.sql

python3 server.py &

SERVER_PID=$!

echo "Server started with PID $SERVER_PID"

sleep 5

pytest --ignore="metadata_tools/tests"

test_result=$?

if [ $test_result -ne 0 ]; then
  echo "Tests failed"
  exit 1
else
  echo "Tests passed"
  exit 0
fi

kill $SERVER_PID

echo "Server with PID $SERVER_PID has been terminated"