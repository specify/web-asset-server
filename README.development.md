Load the complete database backup (all repos, aviable on titan per miro doc):

create_mysql_db.sh

  This will trash and rebuild a docker mysql image and populate it with specify data. 
  It will be on the default database port, 3306

Then, (re)create the images database with:

start_images_development_db.sh

  This will not trash anything existing, but will create a new database on port 3308 
  if one doesn't exist already.

  Then, copy the settings.template.py to settings.py and set the host to your assigned IP number, e.g.:

HOST='192.168.1.223'
And set the database up thusly:

#Image databse connection information
SQL_USER='root'
SQL_PASSWORD='password'
SQL_HOST='127.0.0.1'
SQL_PORT=3308
SQL_DATABASE='images'



  Then, source the env and start the web-images-database 
python3 server.py 


The idea is that specify will be on port 9090, the image server will be on port 80, 
the specify database will be on 3306 and the image database on port 3308.

go to the specify7 directory, cd nginx, edit specify.conf and comment out all services but
the one you want to work on. 

cd ..
docker-compose up

http://localhost:9090/
