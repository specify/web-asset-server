# Institution configuration

1. Copy `settings_local.example.py` to `settings_local.py` beside `settings.py`.
2. Set `HOST` to the public hostname (no `https://` or path), and `KEY` to the same secret used in Specify attachment preferences.
3. Map each exact collection name to its `s3://bucket/prefix` in `COLLECTION_S3_PATHS`. Originals and thumbnails live under `prefix/originals/` and `prefix/thumbnails/`.
4. Configure AWS credentials through the usual boto3 credential chain (for example, an instance IAM role or AWS profile). The server needs permission to read, write, delete, and list the configured objects.
5. Restart the application after changing configuration. Behind HTTPS, configure the reverse proxy to send `X-Forwarded-Proto`.

`settings.py` contains shared defaults. Uppercase values in `settings_local.py` override them; `SERVER_NAME` defaults to the overridden `HOST`, and server/development ports default to `PORT`. You can explicitly override these too.

Keep `settings_local.py` private; Git ignores it. Share the example file instead. The existing local file retains this installation’s production configuration. Without a local file, the defaults have no collection mappings and are not a configured deployment.

For Docker, mount the file read-only at `/home/specify/settings_local.py` for the included Dockerfile. Do not bake secrets into a shared image.
