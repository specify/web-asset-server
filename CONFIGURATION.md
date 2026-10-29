# Institution configuration

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

Uppercase local settings override shared defaults. `SERVER_NAME` defaults to
the overridden `HOST`; server/development ports default to `PORT`.
Restart after changing configuration. For HTTPS, configure the reverse proxy
to send `X-Forwarded-Proto`.

For the included Dockerfile, mount local settings read-only at
`/home/specify/settings_local.py` and mount persistent storage at `BASE_DIR`
when using local mode. Do not bake secrets into shared images.
