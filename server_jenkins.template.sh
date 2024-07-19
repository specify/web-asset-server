#!/bin/bash
image_password="test_password"
python_path=$(pwd)

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

git submodule update --init

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