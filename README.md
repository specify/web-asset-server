Web Asset Server (dans un conténaire)
=====================================

Création d'un conténaire "clef en main" pour le Web Asset Server de Specify.


Requirements 
------------

The requirements are:

1. *Docker* pour la pris en charge du conténaire.
2. Suffisament de *mémoire* (512 Mo) et d'espace disques pour stocker les pièces jointes. 


Installing
----------

Télécharger le conténaire depuis https://hub.docker.com/r/tvalero/web-asset-server/ 

Configuration des variables d'environnements 
--------------------------------------------

SPECIFY_KEY  None

SPECIFY_HOST : nom (DNS) ou adrese (IP) du serveur (hôte)

SPECIFY_PORT : numéro du port sur le serveur (hôte).


Deploying
---------

In my experience, it has been easiest to deploy using the Python *Paste* server.

In `settings.py` set the value `SERVER = 'paste'`.


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


