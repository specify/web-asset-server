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


docker-compose up -d


docker exec -i mysql-images mysql -u root -p"$image_password" -e "CREATE DATABASE IF NOT EXISTS images;"

docker exec -i mysql-images mysql -u root -p"$image_password" images < images_ddl.sql

# Generate SSL certificates at the required paths

# Define the paths for the certificate and key
CERT_PATH="/etc/ssl/certs/wildcard_calacademy_org.pem"
KEY_PATH="/etc/ssl/private/wildcard_calacademy_org.key"

# Check if the certificate and key already exist
if [[ ! -f "$CERT_PATH" && ! -f "$KEY_PATH" ]]; then
    # Generate the SSL certificate and key if they don't exist
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout wildcard_calacademy_org.key \
        -out wildcard_calacademy_org.pem \
        -subj "/C=US/ST=California/L=YourCity/O=YourOrganization/CN=*.calacademy.org"

    # Copy the generated files to the appropriate directories
    sudo cp wildcard_calacademy_org.pem "$CERT_PATH"
    sudo cp wildcard_calacademy_org.key "$KEY_PATH"

    echo "SSL certificate and key created and copied to $CERT_PATH and $KEY_PATH."
else
    echo "SSL certificate and/or key already exist at the specified paths."
fi


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