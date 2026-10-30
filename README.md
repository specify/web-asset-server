# Web Asset Server

Attachment storage for Specify, supporting local files (default) or S3 through
the same attachment API. Docker Compose is the recommended deployment method.

## Deploy with Docker

```sh
install -m 600 settings_local.example.py settings_local.py
# Use a dedicated host group with no unrelated members (choose another name if it exists).
sudo groupadd --system specify-assets
ASSET_GID=$(getent group specify-assets | cut -d: -f3)
# If .env already exists, update its ASSET_GID rather than adding another assignment.
printf 'ASSET_GID=%s\n' "$ASSET_GID" >> .env
sudo chgrp specify-assets settings_local.py
chmod 640 settings_local.py
# Edit settings_local.py for your institution before starting.
docker compose up -d --build
docker compose logs -f asset-server
```

Set a private authentication `KEY` matching Specify attachment preferences,
the public `HOST`, and public `SERVER_PORT`. The included Compose file exposes
port 8080 and mounts `settings_local.py` read-only. Local data persists in the
`attachments` named volume at `/home/specify/attachments`. To reuse existing
files, replace the named volume with a bind mount and grant the configured
container UID and restricted host group read/write access. Keep the container's `PORT` at 8080 unless you also change
the container port mapping.

Use `SERVER_PORT = 8080` for direct HTTP testing, or `SERVER_PORT = 443` behind
a standard HTTPS reverse proxy. The proxy must forward `X-Forwarded-Proto`.
Open `/web_asset_store.xml` at the public address and configure Specify with
that URL and the matching key.

For S3, explicitly set `STORAGE_BACKEND = 's3'`, supply `COLLECTION_S3_PATHS`,
and provide AWS credentials through the runtime credential chain. See
[Configuration](CONFIGURATION.md) for both storage modes.

## Updates and existing deployments

Existing installations should follow [Upgrading](UPGRADING.md) before updating.
Move institution-specific values out of tracked `settings.py` once; subsequent
pulls preserve ignored `settings_local.py`. Configuration precedence is defaults,
environment, then the private file. Private settings are excluded from images.

```sh
git pull --ff-only
docker compose up -d --build
```

Back up configuration and assets before updating and retain the previous image
for rollback. Never remove persistent volumes during an upgrade. Change private
settings on the host, then run `docker compose up -d --force-recreate` to apply
them reliably, including when an editor replaces the file atomically. On Linux,
select a restricted host group, verify that it has no unrelated members, and
set `ASSET_GID` in `.env` to its numeric GID before granting it read access
(`sudo chgrp specify-assets settings_local.py` and `chmod 640 settings_local.py`).
Do not assume host GID 999 is private; the container default may collide with
an existing host group.

## Tests

CI uses Python 3.12 and ImageMagick. On Ubuntu, install ImageMagick with
`sudo apt-get install imagemagick` before running the tests. The `convert`
command is required when importing server routes; the multi-layer TIFF test
also checks for it explicitly.

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The tests use temporary filesystem storage and stubbed S3 operations; no
production credentials or buckets are required.

## License

Web Asset Server is maintained by the Specify Collections Consortium and is
licensed under GNU General Public License version 2. It comes with no warranty.
The Consortium is funded by its member institutions:
[specifysoftware.org](https://www.specifysoftware.org/).
