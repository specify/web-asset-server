Web Asset Server
=========

This is a sample attachment server implementation for Specify. This implementation is targetted at Ubuntu flavors, but will work with minor modifications on other Linux systems. It is not expected to work without extensive adaptation on Windows systems.

The Specify Collections Consortium is funded by its member
institutions. The Consortium web site is:
http://www.specifysoftware.org

Web Asset Server Copyright © 2021 Specify Collections Consortium. Specify
comes with ABSOLUTELY NO WARRANTY.  This is free software licensed
under GNU General Public License 2 (GPL2).

    Specify Collections Consortium
    Biodiversity Institute
    University of Kansas
    1345 Jayhawk Blvd.
    Lawrence, KS 66045 USA


# New features:

* Internal mysql database tracks all imports and allows querying to map a URL 
back to an original filename
  
* Subdirectories created based on the first four letters of the internal filename; prevents very large 
  directory listings
  
* Import client with example specify integration. Import directory trees with files that match a regular 
  expression, descend recursively
  
* Prevents duplicate filename import in a given collection/namespace

* Supports redacted images

* Docker integration with nginx for performance and security

# Installation

## Docker

Docker in the preferred installation method for Web Asset Server.

Example `docker-compose.yml` is provided:

```yaml
version: '3.7'
services:

  asset-server:
    restart: unless-stopped
    image: specifyconsortium/specify-asset-service
    init: true
    volumes:
      # Store all attachments outside the container, in a separate
      # volume
      - "attachments:/home/specify/attachments"
    environment:
      # Replace this with the URL at which asset server would be
      # publicly available
      - SERVER_NAME=host.docker.internal
      - SERVER_PORT=80
      - ATTACHMENT_KEY=your asset server access key
      - DEBUG_MODE=false

volumes:
  attachments: # the asset-servers attachment files
```

## Installing system dependencies



The dependencies are:

1. *Python* 3.6 is known to work. 
1. *ExifRead* for EXIF metadata.
1. *sh* the Python shell command utility.
1. *bottlepy* the Python web micro-framework.
1. *ImageMagick* for thumbnailing.
1. *Ghostscript* for PDF thumbnailing.

To install dependencies
the following commands work on Ubuntu:
```shell
sudo apt-get -y install --no-install-recommends \
  python-pip \
  imagemagick \
  ghostscript
sudo pip install -r requirements.txt
```

## Cloning Web Asset Server source repository
Clone this repository.

```shell
git clone git://github.com/specify/web-asset-server.git
```

## Deployment

Copy  `botany_importer_config.template.py`  `docker-compose.template.yml` and `settings.template.py` to their 
respective filenames without 'template' and adjust settings accordingly. Note that you can run the
system without using docker; simply launch the database with the `start_images_development_db.sh` script
and then run the server with "python3 server.py". This is recommended for initial setup and testing.
Note that for testing, you'll need to use a non-privlidged port such as 8080. 

Once testing is complete, stop the docker container running the database, and type `docker-compose up -d`
to start the full server.

It is important that the working directory is set to the path containing `server.py`
so that *bottle.py* can find the template files. See [“TEMPLATE NOT FOUND” IN MOD_WSGI/MOD_PYTHON](http://bottlepy.org/docs/dev/faq.html#template-not-found-in-mod-wsgi-mod-python).




By default, the server's logs go to standard output which *upstart* will redirect
to `/var/log/upstart/web-asset-server.log`

# Usage


# HTTPS
The easiest way to add HTTPS support, which is necessary to use the asset server with a Specify 7 server that is using HTTPS, is to place the asset server behind a reverse proxy such as Nginx. This also makes it possible to forego *authbind* and run the asset server on an unprivileged port. The proxy must be configured to rewrite the `web_asset_store.xml` resource to adjust the links therein. An example configuration can be found in [this gist](https://gist.github.com/benanhalt/d43a3fa7bf04edfc0bcdc11c612b2278).

# Specify Settings
You will generally want to add the asset server settings to the global Specify 
preferences so that all of the Specify clients obtain the same configuration.

The easiest way to do this is to open the database in Specify and navigate to
the *About* option in the help menu. In the resulting dialog double-click on the
division name under *System Information* on the right hand side. This will open
a properties editor for the global preferences. You will need to set four properties
to configure access to the asset server:

* `USE_GLOBAL_PREFS` - `true`
* `attachment.key` – `##`
   * Replace `##` with the key from the following location:
     * obtain from asset server `settings.py` file if you have a local installation of 7
     * obtain from `docker-compose.yml` file if you use a Docker deployment
* `attachment.url`  `http://[YOUR_SERVER]/web_asset_store.xml` 
* `attachment.use_path` `false`

If these properties do not already exist, they can be added using the *Add Property*
button. 

Compatibility with older versions of Python

# TODO

  * Test with TIFF
  * Test thumbnailing with TIFF
  * convert to universal URLS (n2t.net) and database same (images.universal_urls). Our id=42754. http://n2t.
    net/e/n2t_apidoc.html