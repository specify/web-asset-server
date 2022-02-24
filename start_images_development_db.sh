#!/bin/bash
cd `dirname $0`
curdir=`pwd`
docker run --detatch  --name image-mysql -v $curdir/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=sql_root_password -d mysql:8 -p 3308:3306
