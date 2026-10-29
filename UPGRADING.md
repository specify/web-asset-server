# Upgrade to Docker with local or S3 storage

1. Back up the existing application configuration and attachment data. Record
   the current image tag or commit for rollback. Do not remove the old deployment.
2. Move institution-specific assignments from tracked `settings.py` to an ignored
   `settings_local.py`, using `settings_local.example.py` as a guide. Preserve the
   existing `KEY`, paths, collection mappings, public hostname and public port.
   Set `STORAGE_BACKEND = 's3'` explicitly for S3; local storage is the default.
3. Resolve your old tracked `settings.py` modifications before pulling. Git may
   refuse to merge those modifications: back them up and migrate them deliberately.
   Subsequent pulls preserve `settings_local.py` because it is ignored.
4. Use `docker compose build` and `docker compose up -d`. The included Compose
   file mounts private configuration read-only and persists local attachments.
   To reuse existing filesystem data, replace its named volume with a bind mount
   such as `/srv/existing-attachments:/home/specify/attachments`. Ensure UID/GID
   999 can read/write it. Never use `docker compose down -v` on retained data.
5. Set `SERVER_NAME` and `SERVER_PORT` to the public hostname and port, not the
   container's internal port. Configure HTTPS through your reverse proxy and
   forward `X-Forwarded-Proto`. Verify discovery, an existing original, a thumbnail,
   and a test upload/delete before retiring the old service.

Configuration precedence is defaults, environment, then `settings_local.py`.
The file wins, including over Docker environment variables. Private files are
excluded from image builds. Mount AWS credentials separately or use an IAM role
for S3; they are not stored in the image.

On failure, stop the new container and restore the previous image/service with
its backed-up configuration and the same persistent data. This upgrade does not
migrate or delete existing attachment data.

## Collection mappings

Run the helper on the host so it can atomically replace the private file:

```sh
python3 manage_collection_dirs.py --backend local add collection_name
python3 manage_collection_dirs.py --backend s3 add collection_name s3://bucket/prefix
python3 manage_collection_dirs.py --backend s3 remove collection_name
docker compose up -d --force-recreate asset-server
```

For local per-collection storage, first set `COLLECTION_DIRS = {}`. Keeping it
`None` preserves shared storage. The helper only updates configuration; directories
are created on upload, and removing mappings preserves assets. It never restarts
systemd or contacts S3. Recreating is required after atomic file replacement so
Docker binds the new file rather than retaining the old inode.

The container runs as UID/GID 999. Its private configuration must be readable by
that user. For example, on Linux use `sudo chgrp 999 settings_local.py` and
`chmod 640 settings_local.py`. The helper preserves existing ownership and mode.
New files are created with mode 600; grant container access before deployment.
