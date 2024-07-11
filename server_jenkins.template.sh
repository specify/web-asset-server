#!/bin/bash
image_password="test_password"
python_path="path/to/repository"
echo $(pwd)
echo $PYTHONPATH

setup() {
  echo "Running cleanup..."
  sudo docker stop mysql-images && sudo docker rm mysql-images
  sudo docker stop image-server && sudo docker rm image-server
  sudo docker stop bottle-nginx && sudo docker rm bottle-nginx
  sudo docker image prune -a -f
  sudo rm -rf data/
}

# Call setup at beginning
setup

unset PYTHONPATH

export PYTHONPATH=$python_path:$PYTHONPATH

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

pip install -r requirements.txt

pip install -r metadata_tools/requirements.txt

# git submodule update --init

sudo docker-compose up -d

until sudo docker exec -i mysql-images mysql -u root -p"$image_password" -e "SELECT 1;" &>/dev/null; do
  echo "Waiting for MySQL to be ready..."
  sleep 5
done

sudo cp images_ddl.sql data/

sudo docker exec -i mysql-images mysql -u root -p"$image_password" -e "CREATE DATABASE IF NOT EXISTS images;"

sudo docker exec -i mysql-images mysql -u root -p"$image_password" images < data/images_ddl.sql

sleep 5

sudo pytest --ignore="metadata_tools/tests"

test_result=$?

if [ $test_result -ne 0 ]; then
  echo "Tests failed"
  exit 1
else
  echo "Tests passed"
  # Do not call cleanup here to keep the server up
  exit 0
fi
