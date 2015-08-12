Web Asset Server
================

This is a sample attachment server implementation for Specify.


Dependencies
------------

The dependencies are:

1. *Python* 2.7 is known to work. (see below for Python 2.6)
1. *ExifRead* for EXIF metadata.
1. *sh* the Python shell command utility.
1. *bottlepy* the Python web micro-framework.
1. *ImageMagick* for thumbnailing.
1. *Ghostscript* for PDF thumbnailing.
1. *Paste* Python web server

Bottle is included in the distribution. To install the other dependencies
the following commands work on Ubuntu:

```
sudo apt-get install python-pip imagemagick ghostscript
sudo pip install -r requirements.txt
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

It is important that the working directory is set to the path containing `server.py`
so that *bottle.py* can find the template files. See [“TEMPLATE NOT FOUND” IN MOD_WSGI/MOD_PYTHON](http://bottlepy.org/docs/dev/faq.html#template-not-found-in-mod-wsgi-mod-python).

Note: Some users have reported that `authbind` must be provided with the `--deep` option.
If the asset server is failing to start due to permission problems, this may be a solution.

Then reload the init config files and start the server:

```
sudo initctl reload-configuration
sudo start web-asset-server
```

By default, the server's logs go to standard output which *upstart* will redirect
to `/var/log/upstart/web-asset-server.log`


Specify settings
----------------

You will generally want to add the asset server settings to the global Specify 
preferences so that all of the Specify clients obtain the same configuration.

The easiest way to do this is to open the database in Specify and navigate to
the *About* option in the help menu. In the resulting dialog double-click on the
division name under *System Information* on the right hand side. This will open
a properties editor for the global preferences. You will need to set four properties
to configure access to the asset server:

* `USE_GLOBAL_PREFS` `true`
* `attachment.key`  obtain from asset server `settings.py` file
* `attachment.url`  `http://[YOUR_SERVER]/web_asset_store.xml` 
* `attachment.use_path` `false`

If these properties do not already exist, they can be added using the *Add Property*
button. 

Python 2.6 compatibility
------------------------

The following information is courtesy of David Konrad of The Natural
History Museum of Denmark:

It is possible to install the Attachment Server on a SuSe Enterprise 11 SP3 with python 2.6.8.

* *python-pip* should be installed manually from RPM, v1.2.1 only version that works without conflict / break
* *python-exif* should be installed manually from PRM
* *OrderedDict* needs a "backport" -> https://pypi.python.org/pypi/ordereddict

changes in `server.py`  :

```
try:
    from collections import OrderedDict
except ImportError:
    # python 2.6 or earlier, use backport
    from ordereddict import OrderedDict
```

changes in `settings.py` :

```
#CAN_THUMBNAIL = {'image/jpeg', 'image/gif', 'image/png', 'image/tiff', 'application/pdf'}
CAN_THUMBNAIL = ['image/jpeg', 'image/gif', 'image/png', 'image/tiff', 'application/pdf']
```
