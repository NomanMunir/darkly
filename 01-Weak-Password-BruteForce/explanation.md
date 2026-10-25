# Breach 01 — Weak / guessable password (brute force)

**Flag:** `FLAG{md5_1s_4_n4m3pl4t3_n0t_4_l0ck}`
**Type:** OWASP A07 — Identification & Authentication Failures
**Privilege gate:** this is the **foothold** (anonymous → authenticated `student`).

## How it works
The login form (`POST /login`, fields `identity` + `password`) proxies to the
PocketBase `users` auth collection. There is no rate-limiting, lockout, CAPTCHA
or MFA, so credentials can be guessed online.

The student account `jdoe` never changed its sign-up password. Reconnaissance
gives us everything we need:
- the forum post *"jdoe here… I never changed my signup password"* and replies
  *"run every word in some giant list… yours is near the top of the most famous
  list out there"* — i.e. **rockyou.txt**;
- the staff dashboard and `/api/profile` leak a `pw_hint` field which is simply
  **`md5(password)`** (e.g. `benjamin` → `d7b3e05e072dbee908fdc39db9ab16d7` =
  `md5("b3njamin!")`). Those md5s can also be cracked **offline** — hence the
  flag name: *md5 is a nameplate, not a lock*.

`jdoe`'s password is **`abc123`** — line 10 of rockyou.txt. A few dozen requests
find it. Once authenticated, `GET /api/grades` returns jdoe's own rows and the
`Darkly` project row contains the flag.

## Impact
Full takeover of any account with a weak password, with no detection. Because
the platform *also* exposes `pw_hint = md5(password)`, an attacker who reaches
any user listing (see Breach 00 / 07) can crack passwords **offline** with no
failed-login noise at all.

## Remediation
- Enforce a strong password policy and screen against breach corpora
  (rockyou / HIBP) at registration.
- Add rate-limiting, account lockout / exponential backoff, and ideally MFA.
- **Never store or expose `md5(password)`** (or any password-derived value).
  Use a slow, salted KDF (bcrypt/argon2) and never return it through an API.
