# Breach 05 — Session JWT forgery (hard-coded / leaked secret)

**Flag:** none of its own (this is the escalation **gate** `cadet → admin`; the
`/admin` grades table echoes `FLAG{md5_1s_4_n4m3pl4t3_n0t_4_l0ck}`).
**Type:** OWASP A02 — Cryptographic Failures / A07 — Auth failures.

## How it works
The `session` cookie is a JWT:
```
{"alg":"HS256","typ":"JWT"}.{"sub":"<id>","login":"jdoe","role":"student","exp":...}
```
Its HS256 secret is leaked all over the platform:
- deploy-log comment — *"jwt secret was `42`. wil changed it to `42network`"*;
- the `/internal/config` SSRF dump (Breach 06) — `"jwt_secret":"42network"`.

Mass assignment (Breach 04) caps self-promotion at `cadet`. But with the secret
we can **sign our own token** for any user and role. `/admin` authorises on the
*user's* role (a forged `jdoe/god` token is rejected `403` because jdoe is not
staff/god), so we impersonate the real admin by forging
`sub=<sophie id>, login=sophie, role=god`. The admin panel opens.

The cookie is additionally **not `HttpOnly`** (TODO comment: *"migrate session
cookie to httponly=true — ticket #4201"*), which is what makes the stored-XSS
cookie theft in Breach 08 possible.

## Impact
Complete authentication bypass: any account/role can be impersonated offline,
without a password. This is the step that promotes the audit to full admin.

## Remediation
- Use a long, random, secret key from a secrets manager — never a guessable
  literal, never committed, never returned by any endpoint.
- Prefer server-side sessions, or at least rotate keys and validate `kid`;
  reject `alg:none`.
- Set the session cookie `HttpOnly`, `Secure`, `SameSite=Strict`.
