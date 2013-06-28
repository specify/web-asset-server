Web Asset Server
================

This is a sample attachment server implementation for Specify.


Dependencies
------------

The dependencies are:

1. `Python` 2.7 is known to work.
1. `exif-py` for EXIF metadata.
1. `sh` the Python shell command utility.
1. `bottlepy` the Python web micro-framework.
1. `ImageMagick` for thumbnailing.
1. `Ghostscript` for PDF thumbnailing.

Bottle is included in the distribution. To install the other dependencies
the following commands work on Ubuntu:

```
sudo apt-get install python-exif imagemagick ghostscript
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

Deploying under Apache
----------------------

TBD.

