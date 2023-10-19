#!/bin/bash

# Check if the environment variable 'https' is set to true
if [ "$HTTPS" == "true" ]; then
    sed -i 's/http:\/\//https:\/\//g' web_asset_store.xml
fi

# Execute CMD
exec ve/bin/python server.py
