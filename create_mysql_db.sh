docker container stop mysql-specify; docker container rm mysql-specify
docker  run   -e MYSQL_ROOT_HOST=% -e MYSQL_ROOT_PASSWORD=password --publish 3306:3306 --name=mysql-specify -d mysql/mysql-server:5.7.34
sleep 10
cat startup.sql | mysql -h 127.0.0.1 -u root --password=password -P 3306
cat AllDbsbackup2022-10-01.sql | mysql -h 127.0.0.1 -u root --password=password -P 3306
#cat CASIZbackup2022-10-24.sql | mysql -h 127.0.0.1 -u root --password=password -P 3306 casiz
