---
layout: post
title:  "Deploying My Own Tailscale Server aka Headscale"
date:   2026-07-29 21:00:00
categories: Dev Documentation
tags:
    - Development
    - Documentation
    - DevOps
    - Tailscale
    - Headscale
---

Tailscale is blocked in Oman, so I self-hosted its control server instead. This
is how I deployed [Headscale](https://headscale.net) on my VPS as a Docker Swarm
stack behind Traefik, with its own embedded DERP relay, plus the problems I hit
along the way.

![A tailnet of my laptop, phone, home server and desktop, coordinated by Headscale on a VPS](/postimages/headscale-tailnet.jpg)

## Why

I already run a VPN on my VPS, so why bother? Because I don't want to be
connected to the VPN all the time. Some mobile banking apps in Oman refuse to
work while a VPN is on. What I actually want is "local" access between my own
devices, without routing everything through the VPN.

It also makes developing web apps and games easier, since I often want to test
them from my other devices. I could just open the port and make it reachable on
the local network, but the Wi-Fi isn't only mine. I share it with other people
in my household.

Headscale gives me exactly that: a private network (a "tailnet") between my
devices, using the regular Tailscale clients, with a control server that I run
myself.

## The setup

My VPS already runs everything as Docker Swarm stacks behind Traefik, which also
takes care of the Let's Encrypt certificates. The stack files live in a
`deployment` repo, and `make init-infra` deploys the shared infrastructure. So
Headscale is just one more infra stack:

- `stacks/infra/headscale/config/config.yaml` - the Headscale config
- `stacks/infra/headscale.yml` - the stack file
- one more line in the `Makefile`

It's based on Headscale's
[container install guide](https://headscale.net/stable/setup/install/container/),
using Headscale v0.29.2 and Traefik v3. In the snippets below, replace
`headscale.example.com` with your own domain and `<VPS_PUBLIC_IP>` with your
VPS's public IPv4 address.

### Do I need my own DERP relay?

When two Tailscale devices can't connect to each other directly, they relay
their (still encrypted) traffic through a DERP server. By default, Headscale
hands out Tailscale's public DERP servers, and I wasn't sure those are reachable
from Oman. So I enabled Headscale's embedded DERP server and removed Tailscale's
DERP map, which means my devices only ever use my own relay, on a server I
control.

The DERP relay itself runs over HTTPS, so it goes through Traefik like the rest
of Headscale. The catch is STUN, which clients use to find out their public IP
and port for NAT traversal. It listens on UDP 3478 and can't sit behind a proxy:
STUN has to see the client's real address, and both Traefik and Swarm's routing
mesh would hide it. So UDP 3478 is published directly on the host. It's the one
thing in this setup that bypasses Traefik.

### config.yaml

```yaml
server_url: https://headscale.example.com
listen_addr: 0.0.0.0:8080
metrics_listen_addr: 127.0.0.1:9090
grpc_listen_addr: 127.0.0.1:50443
grpc_allow_insecure: false

noise:
  private_key_path: /var/lib/headscale/noise_private.key

prefixes:
  v4: 100.64.0.0/10
  v6: fd7a:115c:a1e0::/48
  allocation: sequential

database:
  type: sqlite
  sqlite:
    path: /var/lib/headscale/db.sqlite
    write_ahead_log: true

derp:
  server:
    enabled: true
    region_id: 999
    region_code: "headscale"
    region_name: "Headscale Embedded DERP"
    stun_listen_addr: 0.0.0.0:3478
    private_key_path: /var/lib/headscale/derp_server_private.key
    automatically_add_embedded_derp_region: true
    ipv4: <VPS_PUBLIC_IP>
  urls: []
  paths: []
  auto_update_enabled: false
  update_frequency: 24h

disable_check_updates: true

unix_socket: /var/run/headscale/headscale.sock
unix_socket_permission: "0770"

log:
  level: info

dns:
  magic_dns: true
  base_domain: ts.example.com
  override_local_dns: true
  nameservers:
    global:
      - 1.1.1.1
      - 1.0.0.1
  search_domains: []

logtail:
  enabled: false
```

A few things worth pointing out:

- `server_url` is the public URL that clients connect to. Traefik terminates TLS
  and forwards to `listen_addr` on port 8080.
- `derp.server.enabled` turns on the embedded DERP relay and its STUN listener,
  and `ipv4` tells clients where to find it.
- `derp.urls: []` and `derp.paths: []` drop Tailscale's public DERP map, so
  clients only get my relay.
- `dns.base_domain` is the MagicDNS domain for device names. It only resolves
  inside the tailnet, so it doesn't need a real DNS zone.

### headscale.yml

```yaml
version: '3.8'

services:
  headscale:
    image: headscale/headscale:v0.29.2
    command: serve
    ports:
      - target: 3478
        published: 3478
        protocol: udp
        mode: host
    networks:
      - public
    volumes:
      - "/path/to/deployment/stacks/infra/headscale/config:/etc/headscale:ro"
      - headscale_data:/var/lib/headscale
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      restart_policy:
        condition: any
    healthcheck:
      test: ["CMD", "headscale", "health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s
    labels:
      - traefik.enable=true
      - traefik.docker.network=public
      - traefik.http.routers.headscale-http.rule=Host(`headscale.example.com`)
      - traefik.http.routers.headscale-http.entrypoints=web
      - traefik.http.routers.headscale-http.service=headscale
      - traefik.http.routers.headscale-https.rule=Host(`headscale.example.com`)
      - traefik.http.routers.headscale-https.entrypoints=websecure
      - traefik.http.routers.headscale-https.tls.certresolver=myresolver
      - traefik.http.routers.headscale-https.service=headscale
      - traefik.http.services.headscale.loadbalancer.server.port=8080

volumes:
  headscale_data:

networks:
  public:
    external: true
```

- The image is pinned. Headscale still makes breaking config changes between
  releases (see the first problem below), so I don't use `latest`.
- UDP 3478 is published with `mode: host` for STUN, as explained above.
- `traefik.docker.network=public` tells Traefik which network to use to reach
  the container. I added it (and `mode: host`) after a 504 error, more on that
  below.
- The health check uses `headscale health`, because the image is minimal and
  doesn't have `wget` or `curl`.

### Makefile

```makefile
init-infra: ## Create the shared networks and deploy every infra stack
	docker network create -d overlay public || true
	# ...other networks and infra stacks...
	docker stack deploy -c stacks/infra/headscale.yml infra-headscale
```

## Deploying

Before deploying:

1. Add a DNS A record for `headscale.example.com` pointing to the VPS.
2. Open UDP 3478 in your cloud provider's firewall or security group. Publishing
   the port in Docker isn't enough if the provider blocks it before it reaches
   the VPS.

Then deploy and check that it's healthy:

```bash
docker stack deploy -c stacks/infra/headscale.yml infra-headscale
docker service ps infra-headscale_headscale --no-trunc
docker service logs -f infra-headscale_headscale
curl -v https://headscale.example.com/health
```

Healthy means an HTTP 200 with `{"status":"pass"}`. It took me two fixes to get
there.

### Problem 1: `randomize_client_port` was removed

The service kept crashing and restarting, and the logs said:

```
FATAL: The "randomize_client_port" configuration key has been removed. Set "randomizeClientPort": true at the top level of your policy file (see policy.path / policy.mode), or grant the cap per-node via a "nodeAttrs" entry. See CHANGELOG.md (BREAKING / Configuration).
```

My first config still had `randomize_client_port: false`. That option now lives
in the policy file as `randomizeClientPort`. I don't use a policy file, and I
don't need the feature (it makes clients use a random UDP port for WireGuard
instead of a fixed one), so I just deleted the key.

### Problem 2: 504 Gateway Timeout

Once the service stayed up, the health check returned a 504 from Traefik:

```
$ curl -v https://headscale.example.com/health
...
*  SSL certificate verify ok.
...
< HTTP/2 504
Gateway Timeout
```

The certificate was valid, so DNS, Traefik's routing and Let's Encrypt were all
fine. Traefik just couldn't get a response from Headscale. But from the inside,
everything looked healthy:

{% raw %}
```bash
# Docker says the container is "healthy"
docker inspect $(docker ps -q -f name=infra-headscale_headscale) --format "{{json .State.Health}}"

# Traefik's container can reach Headscale by its service name: {"status":"pass"}
docker exec $(docker ps -q -f name=infra-traefik_traefik) wget -qO- http://headscale:8080/health
```
{% endraw %}

So the network path worked. Next, I asked Traefik's API which backend address
it was actually sending requests to (this needs the API enabled in Traefik):

```bash
docker exec $(docker ps -q -f name=infra-traefik_traefik) wget -qO- http://localhost:8080/api/http/services/headscale@docker
```

```json
{
  "loadBalancer": { "servers": [{ "url": "http://10.0.0.115:8080" }] },
  "serverStatus": { "http://10.0.0.115:8080": "UP" }
}
```

That's trimmed, and don't trust the `UP`: without a health check configured in
Traefik, it doesn't actually probe the backend. Calling
`http://10.0.0.115:8080/health` from the Traefik container just hung. So where
does that address come from?

{% raw %}
```bash
docker inspect $(docker ps -q -f name=infra-headscale_headscale) --format '{{json .NetworkSettings.Networks}}'
```
{% endraw %}

```
"ingress": { ... "IPAddress": "10.0.0.115" ... }
"public":  { ... "IPAddress": "10.0.1.147" ... }
```

The container was attached to two networks. `public` is the overlay network
that Traefik shares with my services. `ingress` is Swarm's routing mesh network,
and the container joined it because I had published UDP 3478 in the default
ingress mode. Traefik picked the `ingress` address, but that network only
carries routing mesh traffic, so Traefik's requests hung until it gave up with
a 504.

The fix is these two parts of the stack file:

```yaml
    ports:
      - target: 3478
        published: 3478
        protocol: udp
        mode: host
    # ...
    labels:
      - traefik.docker.network=public
```

`mode: host` takes the container off the `ingress` network (and it's what STUN
needs anyway), and the label makes sure Traefik never has to guess, even if the
container joins more networks later. After redeploying, Traefik's backend moved
to `10.0.1.149` on the `public` network, and the health check finally passed:

```
< HTTP/2 200
< content-type: application/health+json; charset=utf-8
...
{"status":"pass"}
```

## Adding devices

### Create a user and a pre-auth key

On the VPS:

```bash
CID=$(docker ps -q -f name=infra-headscale_headscale)
docker exec -it $CID headscale users create ajiyakin
docker exec -it $CID headscale users list
docker exec -it $CID headscale preauthkeys create --user <USER_ID> --expiration 24h --reusable
```

In this version, `--user` for `preauthkeys create` takes the numeric user ID
from `headscale users list`, not the username. Passing the name fails with:

```
Error: invalid argument "ajiyakin" for "-u, --user" flag: strconv.ParseUint: parsing "ajiyakin": invalid syntax
```

I was also confused by `--expiration` at first. It only limits how long the key
can be used to register new devices. Devices that already joined stay
registered after the key expires, so you don't need a new key every hour. The
flags worth knowing:

- `--expiration 24h` - how long the key can be used to register devices.
- `--reusable` - the key can register more than one device. Without it, the key
  is single-use.
- `--ephemeral` - devices registered with the key are removed automatically
  after they go offline. Good for CI or throwaway machines, not for your own
  devices.

Treat pre-auth keys like passwords: anyone with a valid key can join your
tailnet.

### Join from macOS

```bash
sudo tailscale up --login-server=https://headscale.example.com --authkey=<AUTH_KEY>
```

On my Mac, this first failed with:

```
failed to connect to local Tailscale service; is Tailscale running?
```

I installed Tailscale with Homebrew, which gives you both the `tailscale` CLI
and the `tailscaled` daemon, but doesn't start the daemon. `tailscale up` only
talks to the local daemon, so start it as a background service first (it needs
root), then run `tailscale up` again:

```bash
sudo brew services start tailscale
```

### Or register a device interactively

Without `--authkey`, `tailscale up --login-server=https://headscale.example.com`
prints a login URL instead. Opening it gives you an auth ID
(`hskey-authreq-...`), which you approve on the server:

```bash
docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale auth register --auth-id <AUTH_ID> --user ajiyakin
```

## Testing the connection

On the server, the device should show up:

```bash
docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale nodes list
```

On the device, check the relay. This is the part that answers the "does it work
from Oman" question:

```bash
tailscale netcheck
tailscale status
tailscale ping <OTHER_DEVICE>
```

- `tailscale netcheck` should list the embedded region (`headscale`, ID 999)
  with a real latency instead of a timeout. If it times out, check that UDP 3478
  is open on the VPS side.
- `tailscale ping` shows whether traffic between two devices goes direct or
  through the relay (`via DERP(headscale)`). Either is fine, as long as it
  doesn't time out.

## Cheat sheet

Run on the VPS:

```bash
# list registered devices
docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale nodes list

# approve a device that ran `tailscale up` without an auth key
docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale auth register --auth-id <AUTH_ID> --user ajiyakin

# get the numeric user ID, then create a pre-auth key
docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale users list
docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale preauthkeys create --user <USER_ID> --expiration 24h
```
