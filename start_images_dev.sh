#!/bin/bash
cd `dirname $0`
curdir=`pwd`
docker  run -e MYSQL_ROOT_HOST=% -e MYSQL_ROOT_PASSWORD=password --publish 3310:3306 --name=image_db -d mysql:latest
echo "create database images;" | mysql -u root -p password -h -P 3310
