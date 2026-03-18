# Shared Nginx Notes

On the shared EC2 host, `career-claw` does not run its own public Nginx container. Reuse the existing `didimlog` Nginx and Certbot stack instead.

Recommended `conf.d` layout:

- `default.conf`
- `didim-log.xyz.conf`
- `bot.stdiodh.xyz.conf`
- `claw.stdiodh.xyz.conf`

For `claw.stdiodh.xyz`, use [`claw.stdiodh.xyz.conf.example`](./claw.stdiodh.xyz.conf.example) as the starting point.

Recommended rollout:

1. Add the HTTP server block for `claw.stdiodh.xyz`.
2. Issue the certificate with the existing Certbot/webroot setup.
3. Add the HTTPS server block and reload Nginx.

Useful commands on EC2:

```bash
docker exec didimlog-nginx nginx -t
docker exec didimlog-nginx nginx -s reload
docker ps
```
