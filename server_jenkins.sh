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

python3 -m venv venv

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

ssl_cert_path="/etc/ssl/certs/dynamic_cert.pem"
ssl_key_path="/etc/ssl/private/dynamic_key.pem"

echo "Generating SSL certificates..."
openssl req -newkey rsa:2048 -nodes -keyout "$ssl_key_path" \
    -x509 -days 1 -out "$ssl_cert_path" \
    -subj "/C=US/ST=California/L=San Francisco/O=YourOrg/OU=IT/CN=localhost"

echo "SSL certificates generated at:"
echo "Certificate: $ssl_cert_path"
echo "Key: $ssl_key_path"


python3 server.py > output_log.txt 2>&1 &

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