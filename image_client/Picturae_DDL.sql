# OPEN A Query window for casbotanty and images and run each of these table creation scripts
# before running picturae_import

CREATE TABLE IF NOT EXISTS taxa_unmatch (matchID INTEGER PRIMARY KEY AUTO_INCREMENT,
                                         TimestampCreated VARCHAR(128) NOT NULL ,
                                         TimestampModified VARCHAR(128) NOT NULL ,
                                         batch_MD5 VARCHAR(128),
                                         CatalogNumber VARCHAR(20) NOT NULL ,
                                         fullname VARCHAR(512),
                                         author VARCHAR(128),
                                         name_matched VARCHAR(512),
                                         unmatched_terms VARCHAR(512),
                                         overall_score FLOAT NOT NULL);

CREATE TABLE IF NOT EXISTS picturaetaxa_added (newtaxID INTEGER PRIMARY KEY AUTO_INCREMENT,
                                               TimestampCreated VARCHAR(128) NOT NULL ,
                                               TimestampModified VARCHAR(128) NOT NULL ,
                                               batch_MD5 VARCHAR(128),
                                               CatalogNumber VARCHAR(20) NOT NULL ,
                                               fullname VARCHAR(512),
                                               name varchar(512),
                                               family varchar(512),
                                               hybrid BIT);



CREATE TABLE IF NOT EXISTS  picturae_batch (batchID INTEGER PRIMARY KEY AUTO_INCREMENT,
                                            batch_MD5 VARCHAR(128) NOT NULL ,
                                            TimestampCreated VARCHAR(128) NOT NULL ,
                                            TimestampModified VARCHAR(128) NOT NULL ,
                                            StartTimeStamp TEXT NOT NULL ,
                                            EndTimeStamp TEXT NOT NULL,
                                            batch_size INTEGER);

# DROP TABLE casbotany.picturaetaxa_added;
#
# DROP TABLE casbotany.picturae_batch;
#
# DROP TABLE casbotany.taxa_unmatch;

