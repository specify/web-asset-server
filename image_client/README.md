Web Asset Client 
=========

This is a combination client and server package to provide external web access to 
binary files. The server side will render and cache thumbnails of image format files of any size.
The original server side code was written for specify, and remains compatible with specify.

The server side maintains a minimal database (launchable with the included "launch_db.sh"). 
The database contains: 

ID, original filename, URL, universal url (not used), original path, redacted (boolean), internal_filename,
notes (not used), date added, collection.
155,IMG_8032.jpg,http://192.168.1.224:80/static/botany/originals/d5/48/d548a729-c427-46d1-8407-61254069ba30.jpg,,/Users/joe/Desktop/IMG_8032.jpg,0,d548a729-c427-46d1-8407-61254069ba30.jpg,None,2022-04-12 23:45:04,Botany

Collections must be defined in settings.py. 

## Client usage

### importing
The '-t' flag must be present to DISABLE test mode.

The '-x' flag will let the user specify a regular expression (regex101.com is handy for this!). 
All images that match the regex will be imported from that directory

recursive import '-r' works with -x, but does a recursive descent into any subdirectories.

usage: image-client.py [-h] [-v] collection {search,import} ...

Example; import a single file:
```
./image_client.py Botany import -t /images/botany/test.jpg
```

Example; import a single file:
```
./image_client.py Botany import -t /images/botany/test.jpg
```

### Searching
Searching is SQL style; wildcards are %. Example:

```angular2html
./image_client.py Botany search %8032%
```
```
collection, datetime, id, internal_filename, notes, original filename, original path, redacted, universal URL, URL
Botany,2022-04-12 23:45:04,d548a729-c427-46d1-8407-61254069ba30.jpg,None,IMG_8032.jpg,/Users/joe/Desktop/IMG_8032.jpg,0,None,http://192.168.1.224:80/static/botany/originals/d5/48/d548a729-c427-46d1-8407-61254069ba30.jpg
```

Searching is by collection and can return multiple records. Searching is done against the
original_filename field.

