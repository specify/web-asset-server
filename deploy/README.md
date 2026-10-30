# Docker deployment

1. Install Docker Engine and its Compose plugin.
2. Copy `settings_local.example.py` to `settings_local.py` and configure your institution (see `CONFIGURATION.md`). Keep the application port at 8080 inside the container.
3. Optionally copy `.env.example` to `.env` to configure host paths, port, and file ownership. Private settings and `.env` stay outside Git.
4. Run `docker compose up -d --build`. For AWS credential files, use `docker compose -f docker-compose.yml -f compose.s3.yml up -d --build` instead. Set `AWS_CONFIG_DIR` to their directory and ensure the configured container UID/GID can read them. Instance roles do not require this optional mount; their metadata endpoint must be reachable from containers.

The container restarts after crashes and host reboots when Docker is enabled (`sudo systemctl enable docker`). Nginx or another reverse proxy should forward to localhost:8080 and send `X-Forwarded-Proto`. Logs: `docker compose logs -f`. Deploy updates with the same `up -d --build` command. Restart with `docker compose restart asset-server`.

The default attachment store is a persistent Docker volume. To keep existing local files, set `ASSET_ATTACHMENTS` to their absolute host directory and match its ownership using `ASSET_UID`/`ASSET_GID`. Set `BASE_DIR = '/home/specify/attachments'` in private settings for local storage.

An optional daily restart can be installed using the two timer files here: copy them to `/etc/systemd/system/`, set `WorkingDirectory` in the restart service to your checkout, then run `sudo systemctl daemon-reload && sudo systemctl enable --now web-asset-server-restart.timer`. It runs at 03:00 UTC and briefly interrupts requests. The standard Docker restart policy handles boot and crashes without a custom application systemd service.

## Health checks

Compose checks the `web_asset_store.xml` endpoint every 30 seconds, with a 3-second HTTP timeout, 5-second execution limit, 30-second startup grace period, and three consecutive failures before marking the container unhealthy. The check validates HTTP access and parses the five endpoint definitions without reading or writing assets.

You can see the health with `docker compose ps`. At Specify, we rely on external uptime monitoring for the public HTTPS endpoint to cover nginx (Updown.io), certificates and networking.

## Automatic recovery for unhealthy containers

Install `deploy/watchdog.py` with the checkout, copy `deploy/web-asset-server-watchdog.service` and `.timer` to `/etc/systemd/system/`, and set the service's `WorkingDirectory` to the checkout. Run `sudo systemctl daemon-reload && sudo systemctl enable --now web-asset-server-watchdog.timer`.

The watchdog checks every minute and restarts only a container Docker has marked `unhealthy`. It leaves healthy, starting and deliberately stopped containers alone. Restarts are limited to once per ten minutes, including failed attempts and recent container starts. Set `COOLDOWN_SECONDS` in the service to change this. Attempt timestamps persist under `/var/lib/asset-server-watchdog`. Check activity with `journalctl -u web-asset-server-watchdog.service`. Docker itself does not restart unhealthy containers; this optional watchdog supplies that recovery policy without adding another container.

For named AWS profiles, set `AWS_PROFILE=institution` in `.env` or export it
in the host environment. The S3 Compose override passes that selection into
the container when supplied. Otherwise `AWS_PROFILE` stays unset, preserving
boto3’s normal credential chain (including instance roles); no named profile
is forced.

## Requester identification

Logs include `client_ip` and a user agent limited to 512 characters. User agents
are caller-supplied claims, not verified identities. By default the IP is the
direct connection peer; arbitrary forwarded headers are ignored. Behind nginx,
set `proxy_set_header X-Real-IP $remote_addr;` in every proxied location (nginx
must overwrite the header), then list only nginx's exact connection peer IPs in
`TRUSTED_PROXY_IPS = ['172.18.0.1']` in private settings. The example IP is a
Docker gateway; inspect your network for its actual address. Recreate the
container after changing settings. Do not trust an entire public network.

The Compose health probe identifies itself as `SpecifyAssetHealthcheck/1.0`.
Successful completed loopback probes are omitted from application request logs;
HTTP failures and incomplete responses from identified probes are retained with
`healthcheck: true`. A completed HTTP 200 response is suppressed before the
probe validates its body, so malformed XML or an incorrect URL count can make
Docker mark the probe failed without an application request record. Connection
failures may never reach the application either. Inspect these failures with
`docker inspect --format '{{json .State.Health}}' "$(docker compose ps -q asset-server)"`.
External requests remain logged even when they claim the same user agent.
