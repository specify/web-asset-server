Web Asset Server
=========

This is the official attachment server implementation for Specify. It is designed for Ubuntu flavors but can work with minor modifications on other Linux systems.

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

## Table of Contents

   * [Web Asset Server](#web-asset-server)
     * [Table of Contents](#table-of-contents)
   * [Installation](#installation)
     * [Docker](#docker)
     * [Installing system dependencies](#installing-system-dependencies)
     * [Cloning Web Asset Server source repository](#cloning-web-asset-server-source-repository)
     * [Deployment](#deployment)
       * [Upstart](#upstart)
       * [Systemd](#systemd)
   * [HTTPS](#https)
   * [Specify Settings](#specify-settings)
   * [Compatibility with older versions of Python](#compatibility-with-older-versions-of-python)


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

For production use, it's recommended to also add an nginx web server between
the web asset server and the outside world. Example
[nginx.conf](https://github.com/specify/specify7/blob/393538b081eb797beb502204cdea9311179361f6/nginx.conf#L17-L26)
and [docker-compose.yml](https://github.com/specify/specify7/blob/393538b081eb797beb502204cdea9311179361f6/docker-compose.yml#L126-L135).

For development/evaluation, web asset server can be exposed directly. To do so,
add the following lines to your `docker-compose.yml` right after the `asset-server:` line:
```yaml
    ports:
      - "8080:3306"
```

## Installing system dependencies

The dependencies are:

1. *Python* 3.6 is known to work. ([2.6 and 2.7 is available with modifications](#compatibility-with-older-versions-of-python)).
1. *ExifRead* for EXIF metadata.
1. *sh* the Python shell command utility.
1. *bottlepy* the Python web micro-framework.
1. *ImageMagick* for thumbnailing.
1. *Ghostscript* for PDF thumbnailing.
1. *Paste* Python web server.

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

Adjust the settings in the `settings.py` in your working directory. Then
run the server with the following command:

```shell
python server.py
```

In my experience, it has been easiest to deploy using the Python *Paste* server.

In `settings.py` set the value `SERVER = 'paste'`.

To run the server on a privileged port, e.g. 80, the utility 
[authbind](http://en.wikipedia.org/wiki/Authbind) is recommended.

```shell
sudo apt-get install authbind
```

Assuming you are logged in as the user that will be used to run the server process,
the following commands will tell *authbind* to allow port 80 to be used:

```shell
touch 80
chmod u+x 80
sudo mv 80 /etc/authbind/byport
```

An *upstart* script or *systemd* unit file can be created to make sure the web asset server is started
automatically.

It is important that the working directory is set to the path containing `server.py`
so that *bottle.py* can find the template files. See [“TEMPLATE NOT FOUND” IN MOD_WSGI/MOD_PYTHON](http://bottlepy.org/docs/dev/faq.html#template-not-found-in-mod-wsgi-mod-python).

Note: Some users have reported that `authbind` must be provided with the `--deep` option.
If the asset server is failing to start due to permission problems, this may be a solution.

### Upstart
Create the file `/etc/init/web-asset-server.conf` with the following
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

```shell
sudo initctl reload-configuration
sudo start web-asset-server
```

By default, the server's logs go to standard output which *upstart* will redirect
to `/var/log/upstart/web-asset-server.log`

### Systemd

Create the file `/etc/systemd/system/web-asset-server.conf` with the following
contents, adjusting the usernames and paths as appropriate:

```conf
[Unit]
Description=Specify Web Asset Server
Wants=network.target

[Service]
User=specify
WorkingDirectory=/home/specify/web-asset-server
ExecStart=/usr/bin/authbind /usr/bin/python /home/specify/web-asset-server/server.py
```

Tell Systemd to reload its config with

```shell
sudo systemctl daemon-reload
```


# HTTPS
The easiest way to add HTTPS support, which is necessary to use the asset server with a Specify 7 server that is using HTTPS, is to place the asset server behind a reverse proxy such as Nginx. This also makes it possible to forego *authbind* and run the asset server on an unprivileged port. The proxy must be configured to rewrite the `web_asset_store.xml` resource to adjust the links therein. An example configuration can be found in [this gist](https://gist.github.com/benanhalt/d43a3fa7bf04edfc0bcdc11c612b2278).

# Specify 6 Settings
You will generally want to add the asset server settings to the global Specify preferences so that all of the Specify clients obtain the same configuration.

The easiest way to do this is to open the database in Specify and navigate to the *About* option in the help menu. 

![About Specify](https://user-images.githubusercontent.com/37256050/229819923-fb3a114e-c6fc-4591-8ea2-ae564f4ec099.png)

In the resulting dialog double-click on the **division** name under *System Information* on the right hand side. This will open a properties editor for the global preferences. 

You will need to set four properties to configure access to the asset server:

* `USE_GLOBAL_PREFS` - `true`
* `attachment.key` – `##`
   * Replace `##` with the key from the following location:
     * obtain from asset server `settings.py` file if you have a local installation of 7
     * obtain from `docker-compose.yml` file if you use a Docker deployment
* `attachment.url`  `http://[YOUR_SERVER]/web_asset_store.xml` 
* `attachment.use_path` `false`

If these properties do not already exist, they can be added using the *Add Property* button. 

# Specify 7 Settings

If you are using the [Docker deployment method](https://discourse.specifysoftware.org/t/specify-7-installation-instructions/755#docker-compositions-2), you need to make sure that the `attachment.key` and `attachment.url` match the configuration in Specify 6.

For both the `specify7` and `specify7-worker` sections, you need to make sure that:

- `attachment.key` = `ASSET_SERVER_KEY`
- `attachment.url` = `ASSET_SERVER_URL`

```yml
  specify7:
    restart: unless-stopped
    image: specifyconsortium/specify7-service:v7
    init: true
    volumes:
      - "specify6:/opt/Specify:ro"
      - "static-files:/volumes/static-files"
    environment:
      - DATABASE_HOST=mariadb
      - DATABASE_PORT=3306
      - DATABASE_NAME=specify
      - MASTER_NAME=master
      - MASTER_PASSWORD=master
      - SECRET_KEY=change this to some unique random string
      - ASSET_SERVER_URL=http://host.docker.internal/web_asset_store.xml
      - ASSET_SERVER_KEY=your asset server access key
      - REPORT_RUNNER_HOST=report-runner
      - REPORT_RUNNER_PORT=8080
      - CELERY_BROKER_URL=redis://redis/0
      - CELERY_RESULT_BACKEND=redis://redis/1
      - LOG_LEVEL=WARNING
      - SP7_DEBUG=false
```

If you are using a  local installation, in the `settings.py` file, you need to make sure that:

- `attachment.key` = `WEB_ATTACHMENT_KEY`
- `attachment.url` = `WEB_ATTACHMENT_URL`

```py
# The Specify web attachment server URL.
WEB_ATTACHMENT_URL = None

# The Specify web attachment server key.
WEB_ATTACHMENT_KEY = None
```

# Compatibility with older versions of Python

* [Web Asset server for Python 2.7](https://github.com/specify/web-asset-server)
* [Python 2.6 compatibility](https://github.com/specify/web-asset-server#python-2.6-compatibility)
