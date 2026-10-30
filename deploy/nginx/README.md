# Nginx hardening example

These files are templates, not an automatic production update. Include
`asset-controls.conf` in the `http` context and adapt `assets.example.conf` to
the actual hostname, certificate, and ACME setup. Back up the existing config,
run `sudo nginx -t`, and reload only after compatibility checks pass.

The example enforces HTTPS with a method-preserving 308 redirect. Existing
clients must be tested for HTTP-to-HTTPS redirects, particularly authenticated
POSTs. A redirect cannot protect secrets already sent over HTTP: update Specify
attachment preferences and other clients to use HTTPS directly. Do not enable
HSTS until clients are verified. An HTTP request never reaches the application
except the separately served ACME challenge path.

Recent production logs did not include the request scheme, so they cannot prove
that every older client already uses HTTPS. Browser user agents alone do not
establish compatibility. Verify discovery, original/thumbnail reads, signed
requests, a real upload/delete in a test collection, and Web Portal links using
each supported Specify client version before applying to production.

Defaults: 512 MiB bodies, 60 requests/second/IP with a burst of 120, metadata
2 requests/second/IP with a burst of 6, 32 concurrent requests/IP, 64 per virtual
host, and four concurrent upload requests total. Busy limits return 429.
Adjust for institutions sharing one public IP, bulk imports, and large files.
Timeouts limit inactivity, not total transfer duration. The metadata application
limits are independent of these nginx controls.

For local validation without changing production, copy the complete nginx
configuration tree into a temporary directory, adapt includes to that directory,
and run nginx -t against the temporary main configuration. Do not overwrite
live site files just to syntax-check these templates.
