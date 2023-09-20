#!/bin/bash

cd "$(dirname "$0")"/image_client

if grep -A 20 -B 15 -e "Traceback" -e "Can't parse" "$1"; then
  exit 1
else
  echo pass
  exit 0
fi

