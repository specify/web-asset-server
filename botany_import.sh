#!/usr/bin/bash
cd "$(dirname "$0")"
source ./env/bin/activate
cd image_client
python3 ./client_tools.py -vvvv Botany import >& botany_import_log.txt &


