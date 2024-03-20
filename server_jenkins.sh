#!/bin/bash
image_password="test_password"

echo $(pwd)
echo $PYTHONPATH
cleanup() {
  echo "Running cleanup..."
  docker-compose down
  docker rm mysql-images
  docker rm image-server
  docker rm bottle-nginx
  docker image prune -a
  deactivate
  rm -r data/
}

trap cleanup EXITdocker

if [ ! -d "venv" ]; then
  python3 -m venv venv

  source venv/bin/activate

  pip install -r requirements.txt
else
  source venv/bin/activate

  pip install -r requirements.txt
fi

docker-compose up -d

sleep 5

cp images_ddl.sql data/

docker exec -i mysql-images mysql -u root -p"${image_password}" -e "CREATE DATABASE IF NOT EXISTS images;"

docker exec -i mysql-images mysql -u root -p"${image_password}" images < data/images_ddl.sql

cd tests/ || exit 1

pytest

test_result=$?

if [ $test_result -ne 0 ]; then
  echo "Tests failed"
  exit 1
else
  echo "Tests passed"
  exit 0
fi
