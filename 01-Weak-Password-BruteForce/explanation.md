# Breach 01 — Weak / guessable password (brute force)

**Flag:** `FLAG{md5_1s_4_n4m3pl4t3_n0t_4_l0ck}`
**Type:** OWASP A07 — Identification & Authentication Failures
**Privilege gate:** this is the **foothold** (anonymous → authenticated `student`).

## How it works
The login form (`POST /login`, fields `identity` + `password`) proxies to the
PocketBase `users` auth collection. There is no rate-limiting, lockout, CAPTCHA
or MFA, so credentials can be guessed. The student account `jdoe` never changed
its sign-up password, and reconnaissance tells us exactly who to hit:

- the public forum (no login needed) lists post authors incl. `jdoe`, and jdoe's
  own post *"I never changed my signup password … run every word in some giant
  list against me?"* with replies *"yours is near the top of the most famous
  list out there"* (→ **rockyou.txt**) and *"jdoe's login is the soft target …
  the tutorial account"*;
- the form placeholders give the email shape (`john.doe@42.tech`,
  `you@student.42.tech`), so `jdoe` → **`jdoe@student.42.tech`**.

jdoe's password is **`abc123`** — line 10 of rockyou.txt.

There are **two independent ways** to recover it; both land the same foothold.

### Route A — online brute force (what `exploit.sh` does)
Send password guesses to the live login form, one HTTP request each, and detect
success by the redirect: a failure → `/login?error=Invalid+credentials`, a
success → `/` (plus a `session` cookie). A few dozen requests find `abc123`.
Simple, but noisy (every try is logged) and defeatable by rate-limiting/lockout.

### Route B — offline cracking of the leaked `pw_hint`
Every user record carries a **`pw_hint`** field that is literally
**`md5(password)`**, and the app hands it out. Once you have the hash you never
touch the login form again: you hash wordlist candidates **on your own machine**
and compare. That is the "offline" attack — no requests, no logs, no lockout,
millions of guesses per second.

**Where `pw_hint` comes from (3 sources):**

| Source | Coverage | Form | Needs |
|---|---|---|---|
| `PATCH /api/profile` | **your own** record | **full** 32-hex md5 | any login |
| `GET /staff/dashboard` | **every** user | **truncated** preview (first 13 hex) + tooltip `MD5 — crackable offline` | `cadet` role |
| PocketBase dump (Breach 07) | **every** user | **full** 32-hex md5 for all | PB superuser |

> **Important — use PATCH, not GET.** `/api/profile` is a profile *update*
> endpoint, so it only answers **`PATCH`**. Typing the URL in a browser sends a
> `GET` and returns `{"detail":"Method Not Allowed"}` (HTTP 405). You must send a
> real PATCH request carrying your `session` cookie. An empty body `{}` changes
> nothing but still returns your current record (this same endpoint is abused in
> Breach 04 to also write `"role"`).

Get your own full hash:
```bash
# 1) log in, keep the session cookie
curl -s -c /tmp/j -o /dev/null http://localhost:4942/login \
  --data-urlencode identity=jdoe@student.42.tech --data-urlencode password=abc123
# 2) PATCH (not GET!) /api/profile  ->  returns the record incl. pw_hint
curl -s -b /tmp/j -X PATCH http://localhost:4942/api/profile \
  -H 'Content-Type: application/json' --data '{}'
# => ... "pw_hint":"e99a18c428cb38d5f260853678922e03" ...   (= md5("abc123"))
```
(In the browser you can do the same from DevTools → Console:
`fetch('/api/profile',{method:'PATCH',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.json()).then(console.log)` — the cookie rides along automatically.)

Then crack it offline (hash each candidate locally, compare to the hint):
```bash
printf '%s' abc123 | md5sum          # e99a18c428cb38d5f260853678922e03  -> jdoe
printf '%s' 'b3njamin!' | md5sum      # d7b3e05e072dbee908fdc39db9ab16d7  -> benjamin
# with a wordlist:
#   while read w; do printf '%s %s\n' "$(printf %s "$w"|md5sum|cut -d' ' -f1)" "$w"; done \
#     < rockyou.txt | grep ^<pw_hint>
```
Offline shines where online is hopeless: `benjamin`'s `b3njamin!` sits ~9.8M
lines deep in rockyou — ~9.8M login requests online, but seconds of local
hashing offline.

That `md5(password)` is the point of the flag name — **md5 is a nameplate, not a
lock**: it *labels* the password but, being fast and unsalted, does not protect
it.

## Recovering the flag
Either route authenticates you as `jdoe`. Then `GET /api/grades` returns jdoe's
own rows, and the `Darkly` project row contains the flag.

## Impact
Full takeover of any weak-password account, with no detection. Because the
platform *also* leaks `md5(password)` as `pw_hint`, an attacker who reaches a
user listing can crack passwords **offline** with zero failed-login noise.

## Remediation
- Enforce a strong password policy and screen against breach corpora
  (rockyou / HIBP) at registration.
- Add rate-limiting, account lockout / exponential backoff, and ideally MFA.
- **Never store or expose `md5(password)`** (or any password-derived value).
  Use a slow, salted KDF (bcrypt/argon2) and never return it through an API;
  restrict `/api/profile` to the fields a user may actually read/write.
