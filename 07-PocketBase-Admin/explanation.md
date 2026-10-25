# Breach 07 — PocketBase superuser takeover

**Flag:** `FLAG{th3_und3rsc0r3_sl4sh_kn0ws_th3_w4y}`
**Type:** OWASP A05 — Security Misconfiguration / A01 — Broken Access Control
**Privilege gate:** app-admin → **full backend/database control** (the final gate).

## How it works
The PocketBase backend is directly exposed on `:8090` (leaked by the
`x-pocketbase: http://localhost:8090` response header). Its admin dashboard lives
at **`/_/`** — the flag name *"the underscore-slash knows the way"* points
straight at it, and `robots.txt` even lists `Disallow: /_/`.

The superuser credentials are disclosed by Breach 06's SSRF of
`/internal/config`:
```
pb_admin_email    = admin@42network.local
pb_admin_password = Darkly42Admin!
```
Authenticating (`POST /api/admins/auth-with-password`) yields a superuser token
with full read/write over every collection. `internal_audit` contains the flag
(*"god-tier export OK — flag retained for the security audit"*).

## Impact
Total backend compromise: read/modify every user (password hashes' `pw_hint`,
`recovery_code`, `private_note`), every grade, config, and the ability to create
and download full database **backups** (`POST /api/backups`) — i.e. exfiltrate
the entire datastore.

## Remediation
- Never expose the PocketBase admin API/UI to untrusted networks; bind it to
  loopback or put it behind a VPN/allow-list.
- Rotate the leaked superuser credentials and store them in a secrets manager —
  never in an HTTP-reachable config endpoint.
- Lock down collection API rules (least privilege) and disable the public health
  endpoint from advertising capabilities.
