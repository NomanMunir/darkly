# Breach 03 — IDOR on user profiles

**Flag:** `FLAG{1d0r_ur_pr0f1l3_1s_m1n3}`
**Type:** OWASP A01 — Broken Access Control (Insecure Direct Object Reference)

## How it works
`GET /profile/{id}` renders a user's profile, **including a "Private note" field
that is labelled "Only visible to wil — supposedly."** The handler never checks
that the requester owns the profile, so any authenticated user can read any
other user's private data by changing the `id` in the URL.

The record ids are not secret: they appear in every profile link on
`/staff/dashboard` and in `GET /api/users`. Iterating them and scraping the
rendered page yields `wil`'s private note, which contains the flag.

## Impact
Horizontal and vertical data exposure: any logged-in student can read private
notes (and other per-user fields) of every account, including staff and admin.
Combined with the id enumeration from `/api/users`, it is a one-request-per-user
mass harvest.

## Remediation
- Enforce object-level authorization on every record access: the server must
  verify `session.user == profile.owner` before returning owner-only fields.
- Separate "public profile" fields from "private" fields at the serializer
  level; never render private fields on a route reachable by other users.
- Prefer unguessable ids *and* real authorization (ids alone are not a control).
