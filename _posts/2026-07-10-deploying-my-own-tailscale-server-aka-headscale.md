---
layout: post
title:  "Deploying My Own Tailscale Server aka Headscale"
date:   2026-07-29 21:00:00
categories: Dev Documentation
tags:
    - Development
    - Documentation
---




- Tailscale is blocked in Oman
- I have already have VPN deployed on my vps. The reason I wanted tailscale is to have "local"
  accessibility across my device without havint to always connected to VPN. Because some of
  Oman mobile banking require me to have no VPN connection while accessing their apps.
- Esier for developing some web-based apps and games that I wanted to test from my other devices.
  I can just open the port and let it be accessible from local network, however the WiFi network
  is not only mine, but also shared with other people in my household.



## registering new device into a server
`docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale auth register --auth-id hskey-authreq-AIzeQKAJTcfggZBXHXXAg14X --user ajiyakin`


## listing all connected device from server
`docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale nodes list`






I wanted to deploy headscale as well, can you help me with that? You can see how to deploy headscale with container from this page https://headscale.net/stable/setup/install/container/ and also need to be integrated with traefik if possible (tell me if it is something that is not going to work well or not).

I'll look at the existing infra structure (Traefik config, an existing project stack) to figure out how headscale should fit in.

  Read 2 files, listed 1 directory

⏺ Fetch(https://headscale.net/stable/setup/install/container/)
Received 44.6KB (200 OK)
Invalid tool parameters

⏺ User answered Claude's questions:
· What hostname should Headscale be reachable at (Traefik router + server_url in config.yaml)? → headscale.ajiyakin.com
· Headscale can optionally run its own embedded DERP relay for NAT traversal. It needs a UDP port (STUN) which can't be routed through Traefik/Swarm ingress cleanly - it would need a host-published UDP port bypassing the overlay network. Do you want it enabled? → Does the Tailscale's public DERP blocked in Oman?

I don't have verified, specific data on Oman blocking Tailscale's DERP infrastructure. What I do know generally:

- Oman has a history of restrictive VoIP/VPN policy — unlicensed VPN use has been legally restricted there, and DPI-based blocking of VPN protocols by ISPs (Omantel/Ooredoo) has been reported in the past.
- Tailscale's public DERP relays run on standard cloud IPs (AWS/GCP/etc.) over HTTPS (443), which is harder to selectively block than a dedicated VPN protocol/port — but if Oman is doing deep packet inspection on WireGuard-style traffic in general, Tailscale (which is WireGuard-based) could be affected regardless of DERP.
- I can't confirm current-day behavior from here; the reliable way to know is to actually test connectivity from an Oman network (tailscale netcheck / tailscale ping after joining) once headscale is up.

Given the uncertainty, running your own embedded DERP relay on your VPS (which is presumably outside Oman, or at least a server you control) would sidestep reliance on Tailscale's DERP entirely — traffic would relay through your own server instead. That's actually a reasonable argument for enabling it here, despite the extra Swarm/UDP wiring.

⏺ User answered Claude's questions:
· Given the uncertainty about Tailscale's public DERP being reachable from Oman, how do you want to proceed? → Enable embedded DERP now

⏺ Fetch(https://github.com/juanfont/headscale/releases)
Received 575.7KB (200 OK)

⏺ User answered Claude's questions:
· What is the VPS's public IPv4 address? (needed for the embedded DERP server config so clients know where to reach it) → I'll paste it now

The user chose to paste it — please share the VPS's public IPv4 address so I can bake it into the DERP config.

✻ Churned for 1m 47s

❯ here is the vpn ip address 43.133.137.179

⏺ Fetch(https://raw.githubusercontent.com/juanfont/headscale/v0.29.2/config-example.yaml)
Received 18.3KB (200 OK)

  Ran 1 shell command

⏺ Write(stacks/infra/headscale/config/config.yaml)
Wrote 57 lines to stacks/infra/headscale/config/config.yaml
server_url: https://headscale.ajiyakin.com
listen_addr: 0.0.0.0:8080
metrics_listen_addr: 127.0.0.1:9090
grpc_listen_addr: 127.0.0.1:50443
grpc_allow_insecure: false

noise:
  private_key_path: /var/lib/headscale/noise_private.key

prefixes:
… +47 lines

⏺ Write(stacks/infra/headscale.yml)
Wrote 45 lines to stacks/infra/headscale.yml
version: '3.8'

services:
  headscale:
    image: headscale/headscale:v0.29.2
    command: serve
    ports:
      - target: 3478
        published: 3478
        protocol: udp
… +35 lines

Now updating the Makefile so make init-infra deploys headscale too.

⏺ Update(Makefile)
File must be read first

  Read 1 file

⏺ Update(Makefile)
Added 1 line
  docker stack deploy -c stacks/infra/traefik.yml infra-traefik
  docker stack deploy -c stacks/infra/databases.yml infra-databases
  docker stack deploy -c stacks/infra/waha.yml infra-waha
  docker stack deploy -c stacks/infra/headscale.yml infra-headscale

  Read 1 file

Minimal README, I'll leave it as-is since it's a generic template. Now let me confirm the diff of everything.

  Ran 1 shell command

Setup is ready. Here's what I added:

stacks/infra/headscale.yml — new infra stack (infra-headscale):
- Image headscale/headscale:v0.29.2, single replica pinned to the manager node, same pattern as your other infra stacks.
- Config bind-mounted read-only from stacks/infra/headscale/config/config.yaml, DB/keys on a named volume headscale_data.
- Traefik http/https router pair on headscale.ajiyakin.com, port 8080 — mirrors the existing router convention.
- Embedded DERP relay enabled, with STUN's UDP 3478 published directly on the host (ports: target 3478/udp) since Traefik can't route raw UDP — this is the one thing that sits outside the normal Traefik-only ingress pattern in this repo.

stacks/infra/headscale/config/config.yaml — checked-in config (per this repo's plaintext-secrets convention):
- server_url: https://headscale.ajiyakin.com
- DERP: embedded server on region 999, ipv4: 43.133.137.179, and derp.urls: [] / paths: [] so clients only get your relay, not Tailscale's public ones — since the whole point was avoiding reliance on those from Oman.
- MagicDNS base domain ts.ajiyakin.com (arbitrary — doesn't need a real DNS zone, headscale resolves it internally for the tailnet). Change it if you'd prefer something else.

Makefile — make init-infra now also deploys infra-headscale.

Before running make init-infra, two things to check:
1. Open UDP 3478 in any VPS-level firewall/security group (not just Docker) — same host running Traefik.
2. After deploy, create your first user/preauth key with docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale users create <name> and headscale preauthkeys create -u <name>, then join a client — that'll also tell you whether the embedded DERP is actually reachable from Oman.

One thing I didn't do: add a DNS record for headscale.ajiyakin.com — that's on your DNS provider, outside this repo.

✻ Sautéed for 1m 17s

※ recap: Setting up Headscale as a VPN control server with an embedded DERP relay, integrated into Traefik. Config and stack files are written; next step is running make init-infra and creating the first user/preauth key to test a client connection. (disable recaps in /config)

❯ /commit-staged

  Committed 6b403ee

Committed as 6b403ee: feat(headscale): add headscale infra stack with embedded DERP relay.

✻ Brewed for 8s

※ recap: Set up Headscale as a new infra stack with an embedded DERP relay and committed it. Next: add a DNS record for headscale.ajiyakin.com, then deploy and create your first user/preauth key to test client connectivity from Oman. (disable recaps in /config)

❯ /commit-staged

  Committed 038be09

Committed as 038be09: chore(headscale): deploy headscale stack in make init-infra.

✻ Brewed for 6s

❯ I see this error log on the docker service of headscale when I deploy it:
  ```
  infra-headscale_headscale.1.tudpmuyqprlt@VM-5-39-ubuntu    | 2026-07-10T14:37:37Z FTL
  infra-headscale_headscale.1.tudpmuyqprlt@VM-5-39-ubuntu    | FATAL: The "randomize_client_port" configuration key has been removed. Set "randomizeClientPort": true at the top level of your policy file (see policy.path / policy.mode), or grant the cap per-node via a "nodeAttrs" entry. See CHANGELOG.md (BREAKING / Configuration).
  infra-headscale_headscale.1.tudpmuyqprlt@VM-5-39-ubuntu    |
  infra-headscale_headscale.1.y7bm5mi2abqk@VM-5-39-ubuntu    | 2026-07-10T14:37:31Z FTL
  infra-headscale_headscale.1.y7bm5mi2abqk@VM-5-39-ubuntu    | FATAL: The "randomize_client_port" configuration key has been removed. Set "randomizeClientPort": true at the top level of your policy file (see policy.path / policy.mode), or grant the cap per-node via a "nodeAttrs" entry. See CHANGELOG.md (BREAKING / Configuration).
  infra-headscale_headscale.1.y7bm5mi2abqk@VM-5-39-ubuntu    |
  infra-headscale_headscale.1.iz18lgquq3s6@VM-5-39-ubuntu    | 2026-07-10T14:37:43Z FTL
  infra-headscale_headscale.1.iz18lgquq3s6@VM-5-39-ubuntu    | FATAL: The "randomize_client_port" configuration key has been removed. Set "randomizeClientPort": true at the top level of your policy file (see policy.path / policy.mode), or grant the cap per-node via a "nodeAttrs" entry. See CHANGELOG.md (BREAKING / Configuration).
  infra-headscale_headscale.1.iz18lgquq3s6@VM-5-39-ubuntu    |
  infra-headscale_headscale.1.9mvy778q2suy@VM-5-39-ubuntu    | 2026-07-10T14:37:49Z FTL
  infra-headscale_headscale.1.9mvy778q2suy@VM-5-39-ubuntu    | FATAL: The "randomize_client_port" configuration key has been removed. Set "randomizeClientPort": true at the top level of your policy file (see policy.path / policy.mode), or grant the cap per-node via a "nodeAttrs" entry. See CHANGELOG.md (BREAKING / Configuration).
  infra-headscale_headscale.1.9mvy778q2suy@VM-5-39-ubuntu    |
  infra-headscale_headscale.1.wz3r59zcphah@VM-5-39-ubuntu    | 2026-07-10T14:37:55Z FTL
  infra-headscale_headscale.1.wz3r59zcphah@VM-5-39-ubuntu    | FATAL: The "randomize_client_port" configuration key has been removed. Set "randomizeClientPort": true at the top level of your policy file (see policy.path / policy.mode), or grant the cap per-node via a "nodeAttrs" entry. See CHANGELOG.md (BREAKING / Configuration).
  infra-headscale_headscale.1.wz3r59zcphah@VM-5-39-ubuntu    |
  ```

The randomize_client_port config key was removed upstream in favor of a policy-file setting. Since we don't have a policy file and don't need this feature (it's for randomizing the client's local UDP port to dodge port-based firewall filtering), I'll just remove the key.

  Read 1 file

⏺ Update(stacks/infra/headscale/config/config.yaml)
Removed 2 lines

logtail:
  enabled: false

randomize_client_port: false

Removed the randomize_client_port key — it's no longer a top-level config option in v0.29.2 (moved to the policy file, which we're not using). Redeploy infra-headscale and it should start cleanly.

✻ Worked for 13s

❯ /commit-staged

  Committed f420389

Committed as f420389: fix(headscale): remove obsolete randomize_client_port config key.

✻ Baked for 8s

❯ Now, how can I test it?

Here's a practical test plan, from deploying to confirming a client actually connects through your embedded DERP.

1. Deploy and check the service is healthy
make deploy PROJECT=... # not needed for infra
docker stack deploy -c stacks/infra/headscale.yml infra-headscale
docker service ps infra-headscale_headscale --no-trunc
docker service logs -f infra-headscale_headscale
Look for it settling into Running with no more fatal errors, and confirm the healthcheck passes (docker service inspect or just watch docker service ps for restarts).

2. Confirm Traefik + TLS work
curl -v https://headscale.ajiyakin.com/health
Should return 200 with no cert errors — confirms Traefik routing and Let's Encrypt issuance succeeded. Also verify DNS headscale.ajiyakin.com actually points at the VPS's public IP if you haven't already.

3. Create a user and preauth key
CID=$(docker ps -q -f name=infra-headscale_headscale)
docker exec -it $CID headscale users create myuser
docker exec -it $CID headscale preauthkeys create --user myuser --expiration 1h

4. Join a client (from the machine in Oman, ideally)
Install the Tailscale client, then:
sudo tailscale up --login-server=https://headscale.ajiyakin.com --authkey=<key-from-step-3>

5. Verify the node registered
docker exec -it $CID headscale nodes list

6. Check DERP/relay behavior — this is the part that actually answers the Oman question
tailscale netcheck
tailscale status
tailscale ping <other-node-ip-or-name>
- netcheck should report your custom DERP region (id 999, "headscale") as reachable with a real latency, not a timeout.
- ping between two nodes will tell you via DERP(...) if relayed, or a direct/hairpin path if NAT traversal succeeded. Either is fine — the important thing is it doesn't hang/fail.
- If netcheck can't reach region 999 at all, check that UDP/3478 is actually open on the VPS's firewall/security group (Docker publishing it is necessary but not sufficient).

7. Sanity check STUN externally (from your own machine, not the VPS):
nc -u -zv 43.133.137.179 3478
Confirms the UDP port is reachable from outside before even bringing a client into it.

If you get a real client from Oman connected and netcheck/ping succeed via your region 999, that settles the original blocking concern.

✻ Cogitated for 14s

❯ This is the output:
  ```
  * Host headscale.ajiyakin.com:443 was resolved.
  * IPv6: (none)
  * IPv4: 43.133.137.179
  *   Trying 43.133.137.179:443...
  * Connected to headscale.ajiyakin.com (43.133.137.179) port 443
  * ALPN: curl offers h2,http/1.1
  * (304) (OUT), TLS handshake, Client hello (1):
  *  CAfile: /etc/ssl/cert.pem
  *  CApath: none
  * (304) (IN), TLS handshake, Server hello (2):
  * (304) (IN), TLS handshake, Unknown (8):
  * (304) (IN), TLS handshake, Certificate (11):
  * (304) (IN), TLS handshake, CERT verify (15):
  * (304) (IN), TLS handshake, Finished (20):
  * (304) (OUT), TLS handshake, Finished (20):
  * SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
  * ALPN: server accepted h2
  * Server certificate:
  *  subject: CN=headscale.ajiyakin.com
  *  start date: Jul 10 13:41:04 2026 GMT
  *  expire date: Oct  8 13:41:03 2026 GMT
  *  subjectAltName: host "headscale.ajiyakin.com" matched cert's "headscale.ajiyakin.com"
  *  issuer: C=US; O=Let's Encrypt; CN=YR2
  *  SSL certificate verify ok.
  * using HTTP/2
  * [HTTP/2] [1] OPENED stream for https://headscale.ajiyakin.com/health
  * [HTTP/2] [1] [:method: GET]
  * [HTTP/2] [1] [:scheme: https]
  * [HTTP/2] [1] [:authority: headscale.ajiyakin.com]
  * [HTTP/2] [1] [:path: /health]
  * [HTTP/2] [1] [user-agent: curl/8.7.1]
  * [HTTP/2] [1] [accept: */*]
  > GET /health HTTP/2
  > Host: headscale.ajiyakin.com
  > User-Agent: curl/8.7.1
  > Accept: */*
  >
  * Request completely sent off
  < HTTP/2 504
  < content-length: 15
  < date: Fri, 10 Jul 2026 14:41:07 GMT
  <
  * Connection #0 to host headscale.ajiyakin.com left intact
  Gateway Timeout%
  ```

  of command: `curl -v https://headscale.ajiyakin.com/health`

A 504 from Traefik means the TLS/routing side is fine, but Traefik can't get a response from the headscale container itself. Let's check three things:

  Ran 1 shell command

Please run those four commands on your VPS and paste the output — that'll tell us whether headscale is crash-looping, stuck on the listen_addr: 0.0.0.0:8080 bind, or if it's a Traefik-side discovery issue.

✻ Churned for 23s

❯ Output of command `docker service ps infra-headscale_headscale --no-trunc`:
  ```
  ID                          NAME                              IMAGE                                                                                                 NODE             DESIRED STATE   CURRENT STATE           ERROR                       PORTS
  vo3pxgrl4dv4hcqpt4mzbcyr9   infra-headscale_headscale.1       headscale/headscale:v0.29.2@sha256:d337f1be4a9155b330aa9077bf6c82d24ff0581b8e69390ebc6d7c623bb339ce   VM-5-39-ubuntu   Running         Running 4 minutes ago
  42liueilezv9vloaebtw8a3e1    \_ infra-headscale_headscale.1   headscale/headscale:v0.29.2@sha256:d337f1be4a9155b330aa9077bf6c82d24ff0581b8e69390ebc6d7c623bb339ce   VM-5-39-ubuntu   Shutdown        Failed 4 minutes ago    "task: non-zero exit (1)"
  r3rx1cjb5ugzxauqcd5xtb067    \_ infra-headscale_headscale.1   headscale/headscale:v0.29.2@sha256:d337f1be4a9155b330aa9077bf6c82d24ff0581b8e69390ebc6d7c623bb339ce   VM-5-39-ubuntu   Shutdown        Failed 4 minutes ago    "task: non-zero exit (1)"
  bqj5gxckl4iypp873x6banem4    \_ infra-headscale_headscale.1   headscale/headscale:v0.29.2@sha256:d337f1be4a9155b330aa9077bf6c82d24ff0581b8e69390ebc6d7c623bb339ce   VM-5-39-ubuntu   Shutdown        Failed 4 minutes ago    "task: non-zero exit (1)"
  wbze2c8e2uheui697w7d9k2su    \_ infra-headscale_headscale.1   headscale/headscale:v0.29.2@sha256:d337f1be4a9155b330aa9077bf6c82d24ff0581b8e69390ebc6d7c623bb339ce   VM-5-39-ubuntu   Shutdown        Failed 5 minutes ago    "task: non-zero exit (1)"
  ```

  Output of command `docker service logs -f infra-headscale_headscale`:
  ```
  ID                          NAME                              IMAGE                                                                                                 NODE             DESIRED STATE   CURRENT STATE           ERROR                       PORTS
  vo3pxgrl4dv4hcqpt4mzbcyr9   infra-headscale_headscale.1       headscale/headscale:v0.29.2@sha256:d337f1be4a9155b330aa9077bf6c82d24ff0581b8e69390ebc6d7c623bb339ce   VM-5-39-ubuntu   Running         Running 4 minutes ago
  42liueilezv9vloaebtw8a3e1    \_ infra-headscale_headscale.1   headscale/headscale:v0.29.2@sha256:d337f1be4a9155b330aa9077bf6c82d24ff0581b8e69390ebc6d7c623bb339ce   VM-5-39-ubuntu   Shutdown        Failed 4 minutes ago    "task: non-zero exit (1)"
  r3rx1cjb5ugzxauqcd5xtb067    \_ infra-headscale_headscale.1   headscale/headscale:v0.29.2@sha256:d337f1be4a9155b330aa9077bf6c82d24ff0581b8e69390ebc6d7c623bb33
  ──── (240 lines hidden) ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
           "Isolation": "default"
                  },
                  "Resources": {},
                  "RestartPolicy": {
                      "Condition": "any",
                      "MaxAttempts": 0
                  },
                  "Placement": {
                      "Constraints": [
                          "node.role == manager"
                      ],
                      "Platforms": [
                          {
                              "Architecture": "amd64",
                              "OS": "linux"
                          },
                          {
                              "Architecture": "arm64",
                              "OS": "linux"
                          }
                      ]
                  },
                  "Networks": [
                      {
                          "Target": "6b1trvbt6i4sjg7qstev8etys",
                          "Aliases": [
                              "headscale"
                          ]
                      }
                  ],
                  "ForceUpdate": 0,
                  "Runtime": "container"
              },
              "Mode": {
                  "Replicated": {
                      "Replicas": 1
                  }
              },
              "EndpointSpec": {
                  "Mode": "vip",
                  "Ports": [
                      {
                          "Protocol": "udp",
                          "TargetPort": 3478,
                          "PublishedPort": 3478,
                          "PublishMode": "ingress"
                      }
                  ]
              }
          },
          "Endpoint": {
              "Spec": {
                  "Mode": "vip",
                  "Ports": [
                      {
                          "Protocol": "udp",
                          "TargetPort": 3478,
                          "PublishedPort": 3478,
                          "PublishMode": "ingress"
                      }
                  ]
              },
              "Ports": [
                  {
                      "Protocol": "udp",
                      "TargetPort": 3478,
                      "PublishedPort": 3478,
                      "PublishMode": "ingress"
                  }
              ],
              "VirtualIPs": [
                  {
                      "NetworkID": "ik970sytk5bjb86hhhiu5h9td",
                      "Addr": "10.0.0.96/24"
                  },
                  {
                      "NetworkID": "6b1trvbt6i4sjg7qstev8etys",
                      "Addr": "10.0.1.126/24"
                  }
              ]
          }
      }
  ]
  ```

The container is up and logged listening and serving HTTP on: 0.0.0.0:8080 — headscale itself is fine now. The 504 is Traefik not reaching it. Since a HEALTHCHECK is defined, Traefik may be excluding it from the pool because Docker thinks it's unhealthy. Let's check that plus try hitting it directly from Traefik's container.

  Ran 1 shell command

Please run those five on the VPS and paste back the output.

✻ Brewed for 23s

❯ Output of command `curl -v https://headscale.ajiyakin.com/health`:
  ```
  * Host headscale.ajiyakin.com:443 was resolved.
  * IPv6: (none)
  * IPv4: 43.133.137.179
  *   Trying 43.133.137.179:443...
  * Connected to headscale.ajiyakin.com (43.133.137.179) port 443
  * ALPN: curl offers h2,http/1.1
  * TLSv1.3 (OUT), TLS handshake, Client hello (1):
  *  CAfile: /etc/ssl/certs/ca-certificates.crt
  *  CApath: /etc/ssl/certs
  * TLSv1.3 (IN), TLS handshake, Server hello (2):
  * TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
  * TLSv1.3 (IN), TLS handshake, Certificate (11):
  * TLSv1.3 (IN), TLS handshake, CERT verify (15):
  * TLSv1.3 (IN), TLS handshake, Finished (20):
  * TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
  * TLSv1.3 (OUT), TLS handshake, Finished (20):
  * SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / RSASSA-PSS
  * ALPN: server accepted h2
  * Server certificate:
  *  subject: CN=headscale.ajiyakin.com
  *  start date: Jul 10 13:41:04 2026 GMT
  *  expire date: Oct  8 13:41:03 2026 GMT
  *  subjectAltName: host "headscale.ajiyakin.com" matched cert's "headscale.ajiyakin.com"
  *  issuer: C=US; O=Let's Encrypt; CN=YR2
  *  SSL certificate verify ok.
  *   Certificate level 0: Public key type RSA (4096/152 Bits/secBits), signed using sha256WithRSAEncryption
  *   Certificate level 1: Public key type RSA (2048/112 Bits/secBits), signed using sha256WithRSAEncryption
  *   Certificate level 2: Public key type RSA (4096/152 Bits/secBits), signed using sha256WithRSAEncryption
  *   Certificate level 3: Public key type RSA (4096/152 Bits/secBits), signed using sha256WithRSAEncryption
  * TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
  * using HTTP/2
  * [HTTP/2] [1] OPENED stream for https://headscale.ajiyakin.com/health
  * [HTTP/2] [1] [:method: GET]
  * [HTTP/2] [1] [:scheme: https]
  * [HTTP/2] [1] [:authority: headscale.ajiyakin.com]
  * [HTTP/2] [1] [:path: /health]
  * [HTTP/2] [1] [user-agent: curl/8.5.0]
  * [HTTP/2] [1] [accept: */*]
  > GET /health HTTP/2
  > Host: headscale.ajiyakin.com
  > User-Agent: curl/8.5.0
  > Accept: */*
  >
  < HTTP/2 504
  < content-length: 15
  < date: Fri, 10 Jul 2026 14:48:42 GMT
  <
  * Connection #0 to host headscale.ajiyakin.com left intact
  Gateway Timeout
  ```

  And when I try to create user, it succeed, however this command failed `docker exec -it $CID headscale preauthkeys create --user myuser --expiration 1h`:
  ```
  Error: invalid argument "ajiyakin" for "-u, --user" flag: strconv.ParseUint: parsing "ajiyakin": invalid syntax
  ```

Two separate things here.

Preauth key command — in v0.29.2, --user expects the numeric user ID, not the username (headscale changed user identification to numeric IDs). Get the ID first:

  Ran 1 shell command

504 issue — I still need the diagnostics from my last message to pin this down (you re-ran curl instead). Please run these on the VPS:

  Ran 1 shell command

Please run those five commands on the VPS and paste the output back — that'll tell us whether it's a Docker health-check exclusion or an actual network-reachability problem between Traefik and headscale.

✻ Baked for 17s

❯ Which one is those five commands?

Sorry for the confusion — here they are as plain commands to copy-paste on your VPS, one at a time:

1) Container health status
docker inspect $(docker ps -q -f name=infra-headscale_headscale) --format "{{json .State.Health}}"

2) docker ps with health column
docker ps -f name=infra-headscale_headscale

3) Can headscale reach itself locally
docker exec $(docker ps -q -f name=infra-headscale_headscale) wget -qO- http://127.0.0.1:8080/health; echo

4) Can Traefik reach headscale by its Swarm DNS name
docker exec $(docker ps -q -f name=infra-traefik_traefik) wget -qO- http://headscale:8080/health; echo

5) Full recent Traefik logs
docker service logs infra-traefik_traefik --tail 80

Paste back what each one prints.

✻ Baked for 6s

❯ first command output:
  ```
  {"Status":"healthy","FailingStreak":0,"Log":[{"Start":"2026-07-10T22:50:56.952136925+08:00","End":"2026-07-10T22:50:57.043536871+08:00","ExitCode":0,"Output":"\n"},{"Start":"2026-07-10T22:51:27.044986074+08:00","End":"2026-07-10T22:51:27.145087292+08:00","ExitCode":0,"Output":"\n"},{"Start":"2026-07-10T22:51:57.147084069+08:00","End":"2026-07-10T22:51:57.241178875+08:00","ExitCode":0,"Output":"\n"},{"Start":"2026-07-10T22:52:27.243281824+08:00","End":"2026-07-10T22:52:27.334577075+08:00","ExitCode":0,"Output":"\n"},{"Start":"2026-07-10T22:52:57.336471028+08:00","End":"2026-07-10T22:52:57.430420668+08:00","ExitCode":0,"Output":"\n"}]}
  ```

  second command output:
  ```
  CONTAINER ID   IMAGE                         COMMAND                  CREATED          STATUS                    PORTS     NAMES
  83d281f1f560   headscale/headscale:v0.29.2   "/ko-app/headscale s…"   14 minutes ago   Up 14 minutes (healthy)             infra-headscale_headscale.1.vo3pxgrl4dv4hcqpt4mzbcyr9
  ```

  third output command:
  ```
  OCI runtime exec failed: exec failed: unable to start container process: exec: "wget": executable file not found in $PATH
  ```

  forth command output:
  ```
  {"status":"pass"}
  ```

  5th command output:
  ```
  infra-traefik_traefik.1.59vtwwroriie@VM-5-39-ubuntu    | 2026-07-10T14:34:15Z WRN Traefik can reject some encoded characters in the request path. When your backend is not fully compliant with [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986), it is recommended to set these options to `false` to avoid split-view situation. Refer to the documentation for more details: https://doc.traefik.io/traefik/v3.6/migrate/v3/#encoded-characters-configuration-default-values
  infra-traefik_traefik.1.59vtwwroriie@VM-5-39-ubuntu    | 2026-07-10T14:34:15Z INF Traefik version 3.6.23 built on 2026-07-08T14:24:00Z version=3.6.23
  infra-traefik_traefik.1.59vtwwroriie@VM-5-39-ubuntu    | 2026-07-10T14:34:15Z INF Version check is enabled.
  infra-traefik_traefik.1.59vtwwroriie@VM-5-39-ubuntu    | 2026-07-10T14:34:15Z INF Traefik checks for new releases to notify you if your version is out of date.
  infra-traefik_traefik.1.59vtwwroriie@VM-5-39-ubuntu    | 2026-07-10T14:34:15Z INF It also collects usage data during this process.
  infra-traefik_traefik.1.59vtwwroriie@VM-5-39-ubuntu    | 2026-07-10T14:34:15Z INF Check the documentation to get more info: https://doc.traefik.io/traefik/contributing/data-collection/
  infra-traefik_traefik.1.59vtwwroriie@VM-5-39-ubuntu    |
  ──── (174 lines hidden) ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  =myresolver.acme routerName=nixiza_frontend_internal-https@docker rule=Host(`internal.nixiza.com`)
  infra-traefik_traefik.1.k4a0dco0nqpz@VM-5-39-ubuntu    | 2026-07-10T04:53:41Z INF Testing certificate renew... acmeCA=https://acme-v02.api.letsencrypt.org/directory providerName=myresolver.acme
  infra-traefik_traefik.1.k4a0dco0nqpz@VM-5-39-ubuntu    | 2026-07-10T04:53:42Z WRN A new release of Traefik has been found: 3.7.7. Please consider updating.
  infra-traefik_traefik.1.k4a0dco0nqpz@VM-5-39-ubuntu    | 2026-07-10T04:58:55Z ERR Unable to obtain ACME certificate for domains error="unable to generate a certificate for the domains [internal.nixiza.com]: error: one or more domains had a problem:\n[internal.nixiza.com] invalid authorization: acme: error: 400 :: urn:ietf:params:acme:error:dns :: DNS problem: NXDOMAIN looking up A for internal.nixiza.com - check that a DNS record exists for this domain; DNS problem: NXDOMAIN looking up AAAA for internal.nixiza.com - check that a DNS record exists for this domain\n" ACME CA=https://acme-v02.api.letsencrypt.org/directory acmeCA=https://acme-v02.api.letsencrypt.org/directory domains=["internal.nixiza.com"] providerName=myresolver.acme routerName=nixiza_frontend_internal-https@docker rule=Host(`internal.nixiza.com`)
  infra-traefik_traefik.1.k4a0dco0nqpz@VM-5-39-ubuntu    | 2026-07-10T04:59:04Z ERR Unable to obtain ACME certificate for domains error="unable to generate a certificate for the domains [internal.nixiza.com]: error: one or more domains had a problem:\n[internal.nixiza.com] invalid authorization: acme: error: 400 :: urn:ietf:params:acme:error:dns :: DNS problem: NXDOMAIN looking up A for internal.nixiza.com - check that a DNS record exists for this domain; DNS problem: NXDOMAIN looking up AAAA for internal.nixiza.com - check that a DNS record exists for this domain\n" ACME CA=https://acme-v02.api.letsencrypt.org/directory acmeCA=https://acme-v02.api.letsencrypt.org/directory domains=["internal.nixiza.com"] providerName=myresolver.acme routerName=nixiza_frontend_internal-https@docker rule=Host(`internal.nixiza.com`)
  infra-traefik_traefik.1.k4a0dco0nqpz@VM-5-39-ubuntu    | 2026-07-10T14:34:01Z INF I have to go...
  infra-traefik_traefik.1.k4a0dco0nqpz@VM-5-39-ubuntu    | 2026-07-10T14:34:01Z INF Stopping server gracefully
  infra-traefik_traefik.1.k4a0dco0nqpz@VM-5-39-ubuntu    | 2026-07-10T14:34:03Z INF Server stopped
  infra-traefik_traefik.1.k4a0dco0nqpz@VM-5-39-ubuntu    | 2026-07-10T14:34:03Z INF Shutting down
  ```

  Read 1 file

Reachability from inside the Traefik container to headscale works fine via wget, so the network path is good — but Traefik itself might have picked the wrong backend IP for the service. Since --api.insecure=true is enabled, let's inspect what address Traefik's dynamic config actually resolved for the headscale service:

  Read 1 file

Please run these two on the VPS and paste the output:

docker exec $(docker ps -q -f name=infra-traefik_traefik) wget -qO- http://localhost:8080/api/http/services/headscale@docker; echo
docker exec $(docker ps -q -f name=infra-traefik_traefik) wget -qO- http://localhost:8080/api/http/routers/headscale-https@docker; echo

✻ Crunched for 31s

※ recap: Deploying and testing headscale behind Traefik: it's healthy internally but Traefik returns 504. Next step is running two commands on the VPS to check what backend address Traefik resolved for the headscale service. (disable recaps in /config)

❯ Output of those two commands:
  ```
  {"loadBalancer":{"servers":[{"url":"http://10.0.0.115:8080"}],"strategy":"wrr","passHostHeader":true,"responseForwarding":{"flushInterval":"100ms"}},"status":"enabled","usedBy":["headscale-http@docker","headscale-https@docker"],"name":"headscale@docker","provider":"docker","type":"loadbalancer","serverStatus":{"http://10.0.0.115:8080":"UP"}}
  ```

  ```
  {"entryPoints":["websecure"],"service":"headscale","rule":"Host(`headscale.ajiyakin.com`)","priority":30,"tls":{"options":"default","certResolver":"myresolver"},"observability":{"accessLogs":true,"metrics":true,"tracing":true,"traceVerbosity":"minimal"},"status":"enabled","using":["websecure"],"name":"headscale-https@docker","provider":"docker","priorityStr":"30"}
  ```

  Read 1 file

Run these two on the VPS:

docker exec $(docker ps -q -f name=infra-traefik_traefik) wget -qO- http://10.0.0.115:8080/health; echo
docker inspect $(docker ps -q -f name=infra-headscale_headscale) --format '{{json .NetworkSettings.Networks}}'

This checks whether Traefik's cached backend IP (10.0.0.115) actually matches headscale's current address, or if it's stale from a previous task instance.

✻ Crunched for 13s

❯ The rist command actually got stuck. And here is the second command output:
  ```
  {"ingress":{"IPAMConfig":{"IPv4Address":"10.0.0.115"},"Links":null,"Aliases":null,"DriverOpts":null,"GwPriority":0,"NetworkID":"ik970sytk5bjb86hhhiu5h9td","EndpointID":"096cb7a5df09806966da7cabb7aa69970c81f11f2078c29549b1399f33d15d2b","Gateway":"","IPAddress":"10.0.0.115","MacAddress":"02:42:0a:00:00:73","IPPrefixLen":24,"IPv6Gateway":"","GlobalIPv6Address":"","GlobalIPv6PrefixLen":0,"DNSNames":["infra-headscale_headscale.1.vo3pxgrl4dv4hcqpt4mzbcyr9","83d281f1f560"]},"public":{"IPAMConfig":{"IPv4Address":"10.0.1.147"},"Links":null,"Aliases":null,"DriverOpts":null,"GwPriority":0,"NetworkID":"6b1trvbt6i4sjg7qstev8etys","EndpointID":"e0b3d8c507b85355083cfe634c93aaf7dfe0546ad2d5cdcb0da3df5a9e01490c","Gateway":"","IPAddress":"10.0.1.147","MacAddress":"02:42:0a:00:01:93","IPPrefixLen":24,"IPv6Gateway":"","GlobalIPv6Address":"","GlobalIPv6PrefixLen":0,"DNSNames":["infra-headscale_headscale.1.vo3pxgrl4dv4hcqpt4mzbcyr9","83d281f1f560"]}}
  ```

Found it. Publishing the UDP port in default ingress mode attached the container to Docker's special ingress network (10.0.0.115) in addition to public (10.0.1.147). Traefik's docker provider picked the ingress IP — which isn't reachable from other containers, only used for the routing mesh — hence the 504.

Fix: publish the port in host mode instead (recommended for UDP/STUN anyway, avoids routing-mesh quirks) and add an explicit traefik.docker.network label so Traefik never has to guess.

  Read 1 file

⏺ Update(stacks/infra/headscale.yml)
Added 1 line
      - target: 3478
        published: 3478
        protocol: udp
        mode: host
    networks:
      - public
    volumes:

⏺ Update(stacks/infra/headscale.yml)
Added 1 line
      start_period: 20s
    labels:
      - traefik.enable=true
      - traefik.docker.network=infra-headscale_public
      - traefik.http.routers.headscale-http.rule=Host(`headscale.ajiyakin.com`)
      - traefik.http.routers.headscale-http.entrypoints=web
      - traefik.http.routers.headscale-http.service=headscale

⏺ Update(stacks/infra/headscale.yml)
Added 1 line, removed 1 line
      start_period: 20s
    labels:
      - traefik.enable=true
      - traefik.docker.network=infra-headscale_public
      - traefik.docker.network=public
      - traefik.http.routers.headscale-http.rule=Host(`headscale.ajiyakin.com`)
      - traefik.http.routers.headscale-http.entrypoints=web
      - traefik.http.routers.headscale-http.service=headscale

One more thing — your earlier wget http://10.0.0.115:8080/health command is likely still hanging in your terminal; hit Ctrl+C to kill it before continuing.

Now redeploy and retest:

  Read 1 file

Run these on the VPS from the deployment repo directory:

docker stack deploy -c stacks/infra/headscale.yml infra-headscale
sleep 5
docker exec $(docker ps -q -f name=infra-traefik_traefik) wget -qO- http://localhost:8080/api/http/services/headscale@docker; echo
curl -sv https://headscale.ajiyakin.com/health

The service backend URL should now show 10.0.1.147:8080 (the public network IP) instead of the ingress one, and the curl should return 200 instead of 504.

✻ Sautéed for 37s

❯ Here is the output of those commands:
  ```
  <ps -q -f name=infra-traefik_traefik) wget -qO- http://localhost:8080/api/http/services/headscale@docker; echo
  {"loadBalancer":{"servers":[{"url":"http://10.0.1.149:8080"}],"strategy":"wrr","passHostHeader":true,"responseForwarding":{"flushInterval":"100ms"}},"status":"enabled","usedBy":["headscale-http@docker","headscale-https@docker"],"name":"headscale@docker","provider":"docker","type":"loadbalancer","serverStatus":{"http://10.0.1.149:8080":"UP"}}

  ubuntu@VM-5-39-ubuntu:~/repo/deployment$ curl -sv https://headscale.ajiyakin.com/health
  * Host headscale.ajiyakin.com:443 was resolved.
  * IPv6: (none)
  * IPv4: 43.133.137.179
  *   Trying 43.133.137.179:443...
  * Connected to headscale.ajiyakin.com (43.133.137.179) port 443
  * ALPN: curl offers h2,http/1.1
  * TLSv1.3 (OUT), TLS handshake, Client hello (1):
  *  CAfile: /etc/ssl/certs/ca-certificates.crt
  *  CApath: /etc/ssl/certs
  * TLSv1.3 (IN), TLS handshake, Server hello (2):
  * TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
  * TLSv1.3 (IN), TLS handshake, Certificate (11):
  * TLSv1.3 (IN), TLS handshake, CERT verify (15):
  * TLSv1.3 (IN), TLS handshake, Finished (20):
  * TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
  * TLSv1.3 (OUT), TLS handshake, Finished (20):
  * SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / RSASSA-PSS
  * ALPN: server accepted h2
  * Server certificate:
  *  subject: CN=headscale.ajiyakin.com
  *  start date: Jul 10 13:41:04 2026 GMT
  *  expire date: Oct  8 13:41:03 2026 GMT
  *  subjectAltName: host "headscale.ajiyakin.com" matched cert's "headscale.ajiyakin.com"
  *  issuer: C=US; O=Let's Encrypt; CN=YR2
  *  SSL certificate verify ok.
  *   Certificate level 0: Public key type RSA (4096/152 Bits/secBits), signed using sha256WithRSAEncryption
  *   Certificate level 1: Public key type RSA (2048/112 Bits/secBits), signed using sha256WithRSAEncryption
  *   Certificate level 2: Public key type RSA (4096/152 Bits/secBits), signed using sha256WithRSAEncryption
  *   Certificate level 3: Public key type RSA (4096/152 Bits/secBits), signed using sha256WithRSAEncryption
  * TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
  * using HTTP/2
  * [HTTP/2] [1] OPENED stream for https://headscale.ajiyakin.com/health
  * [HTTP/2] [1] [:method: GET]
  * [HTTP/2] [1] [:scheme: https]
  * [HTTP/2] [1] [:authority: headscale.ajiyakin.com]
  * [HTTP/2] [1] [:path: /health]
  * [HTTP/2] [1] [user-agent: curl/8.5.0]
  * [HTTP/2] [1] [accept: */*]
  > GET /health HTTP/2
  > Host: headscale.ajiyakin.com
  > User-Agent: curl/8.5.0
  > Accept: */*
  >
  < HTTP/2 200
  < content-security-policy: frame-ancestors 'none'
  < content-type: application/health+json; charset=utf-8
  < date: Fri, 10 Jul 2026 15:17:53 GMT
  < referrer-policy: no-referrer
  < x-content-type-options: nosniff
  < x-frame-options: DENY
  < content-length: 18
  <
  {"status":"pass"}
  * Connection #0 to host headscale.ajiyakin.com left intact
  ```

Fixed — 200 {"status":"pass"}. The traefik.docker.network=public + mode: host fix resolved it.

Now let's commit this fix, then continue testing with the preauth key / client join steps.

  Ran 3 shell commands

Ah — it's already committed as b4e3bfe update config (looks like it was auto-committed elsewhere, or you committed it yourself outside our conversation). No pending changes to commit; working tree is clean.

Headscale is now reachable and healthy. Next test steps:

1. Create a preauth key (using the numeric user ID from headscale users list):
docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale users list
docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale preauthkeys create --user <ID> --expiration 1h

2. Join a client (ideally the machine in Oman):
sudo tailscale up --login-server=https://headscale.ajiyakin.com --authkey=<key>

3. Check it registered:
docker exec -it $(docker ps -q -f name=infra-headscale_headscale) headscale nodes list

4. Check DERP relay reachability — this answers the original Oman question:
tailscale netcheck
Look for region 999 (headscale) reporting a real latency rather than a timeout.

Let me know what you get.

✻ Brewed for 20s

※ recap: We're deploying Headscale behind Traefik and it's now working. Next: create a preauth key, join a client (ideally from Oman), and run tailscale netcheck to confirm the embedded DERP relay works.

❯ What does `--expiration 1h` means? Does that means I have to generate auth keys every hour?

No — --expiration 1h only limits how long that preauth key is valid for registering a new node, not how long an already-joined device stays connected.

- Once a device uses the key to join (tailscale up --authkey=...), it's registered permanently (headscale nodes don't expire by default). The key itself becomes irrelevant after that — it's single-use unless you pass --reusable.
- After 1 hour, if you haven't used the key yet, it simply can't be used anymore — you'd need to generate a new one. It does not log out or disconnect existing devices.

Useful flags for preauthkeys create:
- --reusable — lets the same key register multiple devices (handy if you're joining several machines).
- --ephemeral — node gets auto-removed when it disconnects (good for CI/throwaway machines, not what you want for a regular device).
- --expiration 24h / 720h etc. — just gives yourself more time to actually run the tailscale up command before the key goes stale.

For your case (joining your own regular devices), I'd suggest something like --expiration 24h --reusable so you're not rushed, and you can register a couple of test devices with the same key.

✻ Cogitated for 9s

❯ When I ran command `sudo tailscale up --login-server=https://headscale.ajiyakin.com --authkey=hskey-auth-6APmIDUod7zt-CU5qoAG5I-heMwzspsEMZWuduWFbojoeVNz7wV8IA5bXTvTue38mbAl7OXn4fx2V` I got error:
  ```
  failed to connect to local Tailscale service; is Tailscale running?
  ```

That error means the Tailscale client daemon (tailscaled) isn't running on that machine — tailscale up just talks to it locally. What OS is the client machine (the one in Oman) — Linux, macOS, or Windows?

✻ Cogitated for 4s

❯ I use macOS, I installed tailscale via homebrew

The Homebrew tailscale formula only installs the CLI — it doesn't set up tailscaled as a running background service the way the Mac App Store/website version does. You need to start the daemon separately.

  Ran 1 shell command

That confirms it — brew services start tailscale will start tailscaled as a background service (and keep it running across reboots). Run that, then retry your tailscale up command with the authkey.

✻ Cogitated for 9s

※ recap: Setting up headscale behind Traefik, now testing client connectivity via Homebrew tailscale on macOS. Run `brew services start tailscale`, then retry `sudo tailscale up --login-server=https://headscale.ajiyakin.com --authkey=...`
