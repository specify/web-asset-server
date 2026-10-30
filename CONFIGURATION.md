# Institution configuration

## Logging

Application logs are JSON lines on stdout, collected by Docker. View them with
`docker compose logs -f asset-server`. Set `LOG_LEVEL = 'INFO'` in private
settings or `LOG_LEVEL=DEBUG` in the environment (private settings take precedence).
Requests include a generated `X-Request-ID`, route pattern, status, backend,
duration, bytes sent, and completion state. Stream failures and server errors
include exception types and stack locations, without exception messages or locals.
Full query strings, headers and credentials are not logged. Asset requests log allowlisted collection, filename and original/thumbnail type fields; static requests log collection and relative filename. The included
Compose configuration rotates logs at 10 MB and retains three files per container.

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

## Deploying with Docker

See [Docker deployment](deploy/README.md) for the standard Compose setup, optional AWS credential mount, startup on reboot, and daily restart timer. Institution-specific paths and ownership go in ignored `.env`; application settings stay in ignored `settings_local.py`.

Request records distinguish HTTP outcome (`success`, `redirect`, `not_found`, `client_error`, `server_error`) from `response_completed`, which only indicates whether the response body finished sending. Interrupted responses have outcome `transfer_incomplete`. For errors, `bytes_sent` counts the error response body, not asset bytes.

Error summaries include a safe `reason` code: authentication (`missing_token`, `malformed_token`, `expired_token`, `invalid_token`), request validation (`unknown_collection`, `invalid_filename`, `invalid_thumbnail_scale`), storage (`asset_not_found`, `original_not_found`, `asset_changed`, `invalid_storage_configuration`), or metadata (`metadata_date_not_found`). Unclassified errors retain generic status-based reasons. Codes contain no tokens or exception messages.

## Thumbnail load protection

`THUMBNAIL_CONCURRENCY = 1` limits uncached generation per application process.
Cached thumbnails and original downloads bypass it. Up to `THUMBNAIL_QUEUE_SIZE = 5` additional requests wait for a slot for
`THUMBNAIL_QUEUE_WAIT_SECONDS = 20` seconds, allowing normal browser page loads
to complete sequentially. A full queue or expired wait receives HTTP 503 with
`Retry-After: 5` and reason `thumbnail_busy`; bulk clients should retry with
backoff and jitter. The cache is rechecked after waiting to avoid duplicate work. Conversions time out after `THUMBNAIL_TIMEOUT_SECONDS = 60`
with HTTP 504 and reason `thumbnail_timeout`. Increase concurrency only after
measuring memory use. This bounded queue holds existing HTTP requests; it is not a durable background
queue or an automatic client retry mechanism.

ImageMagick uses one thread per conversion and bounded pixel caches:
`THUMBNAIL_MEMORY_LIMIT = '64MiB'`, `THUMBNAIL_MAP_LIMIT = '64MiB'`, and `THUMBNAIL_DISK_LIMIT = '512MiB'`.
