#!/bin/bash

cd "$(dirname "$0")"

if grep -iq "error" ./botany_sync_log.txt; then
  exit 1
else
  exit 0
fi


