#!/bin/bash
cd `dirname $0`
curdir=`pwd`
#docker run -e MYSQL_ROOT_HOST=%  --name image-mysql  -e MYSQL_ROOT_PASSWORD=password -d mysql:latest -p 3308:3306
docker  run   -e MYSQL_ROOT_HOST=% -e MYSQL_ROOT_PASSWORD=password --publish 3308:3306 --name=image-mysql -d mysql:latest
