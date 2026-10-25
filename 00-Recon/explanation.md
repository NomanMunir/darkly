# Breach 00 — Reconnaissance & information disclosure

**Flag:** none (this is the recon pass; it enables the rest).
**Type:** OWASP A05 — Security Misconfiguration / A01 — Broken Access Control

## What the platform leaks for free
- **Debug/fingerprint headers** on every response:
  `server: uvicorn`, `x-powered-by: Python/3.11 FastAPI/0.104`,
  `x-pocketbase: http://localhost:8090` (reveals the backend → Breach 07),
  `x-42-internal: campus=paris`.
- **`robots.txt`** lists the "secret" areas: `/admin /staff /internal /backup
  /api/grades /_/ /static/uploads/` — i.e. a map of what to attack.
- **HTML source comments** across pages are a running commentary of every bug:
  SQL/SQLi history, non-HttpOnly session cookie, `xml.etree` instead of
  defusedxml, `/internal/config` localhost-only, the JWT secret history
  (`"42"` → `"42network"`), md5 password hints, etc.
- A **base64 string** hidden in a forum post (hint: *"Base64 is not encryption.
  It's a costume"*): `dmFsaWRhdGlvbl9rZXk9NDJuZXR3b3Jr` →
  `validation_key=42network`. Sending `X-Validation-Key: 42network` to `/backup`
  unlocks debug backup metadata headers (`x-backup-dest`,
  `x-backup-exclude: data/private_notes.txt`, …).
- **`/api/docs-internal`** (any logged-in user) documents the data model,
  including that `role` is writable via `PATCH /api/profile` (→ Breach 04) and
  that `grades` has a `flag` field read via `/api/grades` (→ Breaches 01/10).
- **`/staff/dashboard`** prints a users table including each user's `pw_hint`
  (= `md5(password)`), enabling offline cracking (→ Breach 01).

## Impact
Each leak removes guesswork and directly enables a later breach: the backend
location, the privilege model, the JWT secret, the weak-credential hints and the
internal endpoints are all handed to an unauthenticated visitor.

## Remediation
- Strip server/framework/debug headers; don't advertise the backend.
- Don't ship source comments or `/api/docs-internal` to production; treat
  `robots.txt` as a hint to attackers, not a control.
- Remove the base64 "secret", the `/backup` debug headers, and the `pw_hint`
  column; keep internal docs behind real auth.
