#!/bin/bash
# cleanup lockfile on exit
source ./server_jenkins_config.sh

trap cleanup EXIT


# checking lock

exec 200>$lockfile
flock -n 200 || { echo "Another instance of the script is already running. Exiting."; exit 1; }

unset PYTHONPATH

export PYTHONPATH=$python_path:$PYTHONPATH

echo $PYTHONPATH

rm -r venv

sleep 5

python3.12 -m venv venv

source venv/bin/activate

# Print Python version
echo "Python version:"
python --version

# Upgrade pip and install requirements

git config --global --add safe.directory "$(pwd)"

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

# replace https with http in pytest and xml files
convert_to_http

# run server
python3 server.py > output_file.txt 2>&1 &
# Give the server some time to initialize
sleep 5

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