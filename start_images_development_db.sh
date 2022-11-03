#!/bin/bash
cd `dirname $0`
curdir=`pwd`
docker  run   -e MYSQL_ROOT_HOST=% -e MYSQL_ROOT_PASSWORD=password --publish 3308:3306 --name=image-mysql -d mysql:latest
echo "create database images;" | mysql -u root -ppassword -h 127.0.0.1 -P 3308
