#!/usr/bin/bash
cd "$(dirname "$0")"
source ./env/bin/activate
cd image_client
python3 ./client_tools.py Ichthyology import >& ichthyology_import_log.txt &

