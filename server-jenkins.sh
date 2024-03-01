#!/bin/bash

sudo docker-compose up -d
(
cd tests/ || return

pytest

if [ $? -ne 0 ]; then
  echo "Tests failed"
  exit 1
fi
echo "Tests passed"
)

sudo docker-compose down
