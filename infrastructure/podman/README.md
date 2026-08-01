# Podman deployment

Copy the Quadlet files into `~/.config/containers/systemd/`, create the
environment files referenced by the containers, then run:

```sh
systemctl --user daemon-reload
systemctl --user enable --now personal-website.target
loginctl enable-linger "$USER"
```

The API is bound to localhost so Cloudflare Tunnel can be the only public
entry point. The current bootstrap builds the image directly on the homelab;
CI can publish the same image to GHCR once the deployment workflow is added.

## Cloudflare Tunnel

Create `~/.config/personal-website/cloudflared.env` on the homelab with the
tunnel token supplied by Cloudflare. Do not commit this file:

```text
TUNNEL_TOKEN=replace-with-the-token-from-cloudflare
```

Copy `cloudflared.container` into the Quadlet directory, reload systemd, and
start it with `systemctl --user start cloudflared.service`. Configure the
tunnel hostname `api.mayankp.me` to route to
`http://personal-website-api:8000` in Cloudflare Zero Trust.
