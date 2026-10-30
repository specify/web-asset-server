# Docker deployment

1. Install Docker Engine and its Compose plugin.
2. Copy `settings_local.example.py` to `settings_local.py` and configure your institution (see `CONFIGURATION.md`). Keep the application port at 8080 inside the container.
3. Optionally copy `.env.example` to `.env` to configure host paths, port, and file ownership. Private settings and `.env` stay outside Git.
4. Run `docker compose up -d --build`. For AWS credential files, use `docker compose -f docker-compose.yml -f compose.s3.yml up -d --build` instead. Set `AWS_CONFIG_DIR` to their directory and ensure the configured container UID/GID can read them. Instance roles do not require this optional mount; their metadata endpoint must be reachable from containers.

The container restarts after crashes and host reboots when Docker is enabled (`sudo systemctl enable docker`). Nginx or another reverse proxy should forward to localhost:8080 and send `X-Forwarded-Proto`. Logs: `docker compose logs -f`. Deploy updates with the same `up -d --build` command. Restart with `docker compose restart asset-server`.

The default attachment store is a persistent Docker volume. To keep existing local files, set `ASSET_ATTACHMENTS` to their absolute host directory and match its ownership using `ASSET_UID`/`ASSET_GID`. Set `BASE_DIR = '/home/specify/attachments'` in private settings for local storage.

An optional daily restart can be installed using the two timer files here: copy them to `/etc/systemd/system/`, set `WorkingDirectory` in the restart service to your checkout, then run `sudo systemctl daemon-reload && sudo systemctl enable --now web-asset-server-restart.timer`. It runs at 03:00 UTC and briefly interrupts requests. The standard Docker restart policy handles boot and crashes without a custom application systemd service.
