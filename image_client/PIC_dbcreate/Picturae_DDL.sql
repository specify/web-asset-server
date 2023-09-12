# OPEN A Query window for casbotanty and images and run each of these table creation scripts
# before running picturae_import
# chmod +x image_client/create_pic_db.txt
# docker run --name picbatch-mysql -e MYSQL_ROOT_PASSWORD=D1g1tiz3r -e MYSQL_DATABASE=picbatch -d -p 3309:3306 mysql
# docker cp image_client/Picturae_DDL.sql picbatch-mysql:/usr/lib/mysql
# docker exec -it picbatch-mysql bash
# mysql -u root -p
# USE picbatch;
# SOURCE /usr/lib/mysql/Picturae_DDL.sql;
# exit;
# exit

CREATE TABLE IF NOT EXISTS picbatch.taxa_unmatch (matchID INTEGER PRIMARY KEY AUTO_INCREMENT,
                                         TimestampCreated VARCHAR(128) NOT NULL ,
                                         TimestampModified VARCHAR(128) NOT NULL ,
                                         batch_MD5 VARCHAR(128),
                                         CatalogNumber VARCHAR(20) NOT NULL ,
                                         fullname VARCHAR(512),
                                         author VARCHAR(128),
                                         name_matched VARCHAR(512),
                                         unmatched_terms VARCHAR(512),
                                         overall_score FLOAT NOT NULL);

CREATE TABLE IF NOT EXISTS picbatch.picturaetaxa_added (newtaxID INTEGER PRIMARY KEY AUTO_INCREMENT,
                                                        TimestampCreated VARCHAR(128) NOT NULL ,
                                                        TimestampModified VARCHAR(128) NOT NULL ,
                                                        batch_MD5 VARCHAR(128),
                                                        CatalogNumber VARCHAR(20) NOT NULL ,
                                                        fullname VARCHAR(512),
                                                        name varchar(512),
                                                        family varchar(512),
                                                        hybrid BIT);



CREATE TABLE IF NOT EXISTS  picbatch.picturae_batch (batchID INTEGER PRIMARY KEY AUTO_INCREMENT,
                                                     batch_MD5 VARCHAR(128) NOT NULL ,
                                                     TimestampCreated VARCHAR(128) NOT NULL ,
                                                     TimestampModified VARCHAR(128) NOT NULL ,
                                                     StartTimeStamp TEXT NOT NULL ,
                                                     EndTimeStamp TEXT NOT NULL,
                                                     batch_size INTEGER);
#
# DROP TABLE picturaetaxa_added;
# #
# DROP TABLE picturae_batch;
# #
# DROP TABLE taxa_unmatch;

