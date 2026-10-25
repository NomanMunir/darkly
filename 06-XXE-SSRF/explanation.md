# Breach 06 — XXE → SSRF (reads the localhost-only internal config)

**Flag:** `FLAG{d3fus3dxml_n3xt_spr1nt_pr0m1s3}`
**Type:** OWASP A05 — Security Misconfiguration / A03 — Injection (XXE) / SSRF

## How it works
`/agenda/import` accepts an XML file and parses it with external entities
enabled. The platform admits it: deploy log *"disabled defusedxml temporarily
(that was 6 months ago)"*, staff page tag *"stdlib ET (unsafe)"*, agenda note
*"the importer parses any XML you upload, entities and all."*

Testing shows the parser resolves **external entities over HTTP** (an external
`SYSTEM "http://…"` entity triggers a server-side fetch; verified out-of-band).
That turns XXE into **SSRF**. The endpoint `/internal/config` is blocked for
remote clients (`403 forbidden`, checked on the peer IP), but when the *server*
fetches it the request comes from `127.0.0.1` and passes. The resolved entity is
reflected in the imported event's title, so we read the response directly:

```json
{"jwt_secret":"42network","pb_admin_email":"admin@42network.local",
 "pb_admin_password":"Darkly42Admin!","app_version":"1.0.0",
 "campus":"wilcity","darkly_flag":"FLAG{d3fus3dxml_n3xt_spr1nt_pr0m1s3}"}
```

That single response yields the flag **and** the JWT secret (→ Breach 05) **and**
the PocketBase admin credentials (→ Breach 07).

> Note: `file://` entities return empty on this build (so classic local-file
> read is blocked), but HTTP external entities work — the exploitable primitive
> here is SSRF, not arbitrary file read.

## Impact
Internal-only configuration disclosure leading to full compromise: the JWT
signing key and database-admin credentials are handed to any authenticated user.
SSRF also lets the server be aimed at other internal endpoints.

## Remediation
- Parse XML with a hardened library (`defusedxml`): disable DTDs, external
  entities and network access (`resolve_entities=False`, `no_network=True`).
- Don't rely on "localhost only" as a security boundary reachable via SSRF; add
  real authentication/authorization to `/internal/config` and keep secrets out
  of any HTTP-reachable endpoint.
- Restrict outbound requests the parser/app can make (egress allow-list).
