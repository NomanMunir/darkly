# Breach 04 — Privilege escalation via mass assignment

**Flag:** `FLAG{just_p4tch_y0ur_0wn_r0l3_lol}`
**Type:** OWASP A01 — Broken Access Control / A08 — Mass assignment
**Privilege gate:** `student → cadet`.

## How it works
`PATCH /api/profile` is meant to let a user edit harmless fields (first name,
campus, avatar). The handler blindly binds the JSON body to the user record,
including the **`role`** field. `/api/docs-internal` even documents it:
`"writable_fields":[...,"role"]`, `"role_values":["visitor","student","cadet",
"staff","god"]`, `"note":"role writable via PATCH /api/profile"`.

So a `student` sends `{"role":"cadet"}` and is promoted. Re-authenticating
issues a fresh session JWT carrying `"role":"cadet"`, which unlocks the staff
area; `/staff/dashboard` then shows the flag.

The allow-list does stop a direct jump to the top: `{"role":"staff"}` /
`{"role":"god"}` return `{"error":"role not assignable"}`. Reaching those
levels is the next link in the chain → **Breach 05 (JWT forgery)**. (The same
endpoint is also over-permissive about other fields — `level`, `verified`,
`private_note`, `recovery_code` are all writable — which is a mass-assignment
problem in its own right.)

> **Same endpoint, abused two ways — and it is `PATCH`-only.** `/api/profile` is
> the single profile *update* route, so it answers **`PATCH`**, not `GET`
> (a browser address-bar `GET /api/profile` returns `405 Method Not Allowed`).
> Every request must carry your `session` cookie. **Breach 01 *reads* its
> response** — even an empty-body PATCH `{}` returns your full record, leaking
> `pw_hint = md5(password)` — while **Breach 04 *writes* to it** to set `role`.
> One over-trusting update endpoint is therefore both an information-disclosure
> sink (Breach 01) and a privilege-escalation sink (this breach).

```bash
# read path (Breach 01): leaks your own pw_hint = md5(password)
curl -s -b /tmp/j -X PATCH http://localhost:4942/api/profile \
  -H 'Content-Type: application/json' --data '{}'
# write path (Breach 04): escalates your own role
curl -s -b /tmp/j -X PATCH http://localhost:4942/api/profile \
  -H 'Content-Type: application/json' --data '{"role":"cadet"}'
```

## Impact
Vertical privilege escalation from a normal student to cadet/staff tooling
(student management, newsletter admin, file upload, XML import) with a single
authenticated request.

## Remediation
- Never bind request bodies directly to data models. Use an explicit allow-list
  of **non-privileged** fields; `role`, `level`, `verified`, etc. must only be
  settable by an authorized admin workflow, server-side.
- Derive authorization from a trusted server-side value, not from a field the
  user can write.
