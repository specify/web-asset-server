
docker run --name picbatch-mysql -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=picbatch -d -p 3309:3306 mysql
docker cp image_client/PIC_dbcreate/Picturae_DDL.sql picbatch-mysql:/usr/lib/mysql
docker exec -it picbatch-mysql bash
mysql -u root -p
USE picbatch;
SOURCE /usr/lib/mysql/Picturae_DDL.sql;
exit;
exit