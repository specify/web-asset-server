# Institution configuration

S3 downloads stream in 64 KiB chunks and support HEAD and single byte ranges
(including open-ended and suffix ranges). Unsatisfiable ranges return 416;
multipart ranges fall back to a full response. If-Range honors an exact ETag or
Last-Modified value. Thumbnail inputs are streamed to isolated temporary files.

Copy `settings_local.example.py` to `settings_local.py` beside `settings.py`.
Set `HOST` to the public hostname (without scheme or path), and `KEY` to the
secret configured in Specify attachment preferences. Keep this file private;
Git ignores it.

## Local storage (default)

Set `BASE_DIR` to a writable directory, such as `/srv/attachments`.
With `COLLECTION_DIRS = None`, all collections share its `originals/` and
`thumbnails/` directories. To isolate collections, set
`COLLECTION_DIRS = {'Example Collection': 'example'}`; each relative directory
contains its own `originals/` and `thumbnails/`. No AWS credentials are used.

## S3 storage (optional)

Set `STORAGE_BACKEND = 's3'` explicitly and define `COLLECTION_S3_PATHS` using
exact collection names and `s3://bucket/prefix` values. Objects are stored under
`prefix/originals/` and `prefix/thumbnails/`. Configure AWS credentials through
the boto3 credential chain, such as an instance IAM role or AWS profile, with
read, write, delete, and list permissions for those objects.

S3 deployments upgrading from automatic selection must add
`STORAGE_BACKEND = 's3'` before restarting; collection mappings alone no longer
select S3. Invalid backend values cause startup to fail.

## Server settings

Precedence is shared defaults, environment variables, then the private file.
Uppercase local settings override both defaults and environment. `SERVER_NAME` defaults to
the overridden `HOST`; server/development ports default to `PORT`.
Set `SERVER_PORT` to the public port (443 for standard HTTPS).
Run `docker compose up -d --force-recreate` after changing configuration.
The private file must be readable by container UID/GID 999; on Linux, one option
is `sudo chgrp 999 settings_local.py` followed by `chmod 640 settings_local.py`.
For HTTPS, configure the reverse proxy
to send `X-Forwarded-Proto`.

For the included Dockerfile, mount local settings read-only at
`/home/specify/settings_local.py` and mount persistent storage at `BASE_DIR`
when using local mode. Do not bake secrets into shared images.
