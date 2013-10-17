Web Asset Server
================

This is a sample attachment server implementation for Specify.


Dependencies
------------

The dependencies are:

1. *Python* 2.7 is known to work.
1. *exif-py* for EXIF metadata.
1. *sh* the Python shell command utility.
1. *bottlepy* the Python web micro-framework.
1. *ImageMagick* for thumbnailing.
1. *Ghostscript* for PDF thumbnailing.

Bottle is included in the distribution. To install the other dependencies
the following commands work on Ubuntu:

```
sudo apt-get install python-exif python-pip imagemagick ghostscript
sudo pip install sh
```

Installing
----------

It is easiest just to clone this repository.

Running the development server
------------------------------

Adjust the settings in the `settings.py` in your working directory. Then
run the server with the following command:

```
python server.py
```

Deploying
---------

In my experience, it has been easiest to deploy using the Python *Paste* server.

`sudo apt-get install python-paste`

In `settings.py` set the value `SERVER = 'paste'`.

To run the server on a privileged port, e.g. 80, the utility 
[authbind](http://en.wikipedia.org/wiki/Authbind) is recommended.

`sudo apt-get install authbind`

Assuming you are logged in as the user that will be used to run the server process,
the following commands will tell *authbind* to allow port 80 to be used:

```
touch 80
chmod u+x 80
sudo mv 80 /etc/authbind/byport
```

An *upstart* script can be created to make sure the web asset server is started
automatically. Create the file `/etc/init/web-asset-server.conf` with the following
contents, adjusting the `setuid` user and directories as appropriate:

```
description "Specify Web Asset Server"
author "Ben Anhalt <anhalt@ku.edu>"

start on runlevel [234]
stop on runlevel [0156]

setuid anhalt

chdir /home/anhalt/web-asset-server
exec /usr/bin/authbind /usr/bin/python /home/anhalt/web-asset-server/server.py
respawn
```

Then reload the init config files and start the server:

```
sudo initctl reload-configuration
sudo start web-asset-server
```

By default, the server's logs go to standard output which *upstart* will redirect
to `/var/log/upstart/web-asset-server.log`


Specify settings
----------------

To set up a Specify client to use the server, set the Server URL and Key in the
Attachment Preferences. The URL will be `http://[YOUR_SERVER]/web_asset_store.xml`.
For the key, use the same value as in the server `setting.py` file.
