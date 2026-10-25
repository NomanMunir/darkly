# Breach 02 — Broken password-reset flow

**Flag:** `FLAG{r3s3t_t0k3n_w4s_just_md5_lol}`
**Type:** OWASP A07 — Identification & Authentication Failures / Insecure design

## How it works
Two independent, critical flaws in one feature:

1. **The reset token is leaked to the requester.** `POST /reset-password/request`
   responds `302` to
   `/reset-password?email=<e>&token=<32-hex>` — the token is handed straight to
   whoever asks, instead of being emailed to the account owner. It works for any
   address, even ones that don't exist.

2. **The token is predictable.** It is exactly `md5(email)`:
   `md5("benjamin@student.42.tech") = f1640a02eeccb971463836da7300b3ba`, which is
   the value returned. So the token can be computed offline — no request needed.

Either flaw alone is a full account-takeover primitive. `POST
/reset-password/confirm` (email + token + `new_password`) then sets the password.
After logging in as the victim, `/profile/me/settings` displays the account
**recovery code**, which holds the flag (forum PSA: *"once they're in, your
account recovery code is just sitting there on your profile settings page"*).

## Impact
Any account — including staff/admin (`wil`, `sophie`) — can be taken over by an
unauthenticated attacker who only knows (or guesses) the email address.

## Remediation
- Generate reset tokens from a CSPRNG, store only their hash, bind them to the
  user + an expiry, and make them single-use.
- **Deliver the token out-of-band** (email); never return it in the HTTP
  response/redirect.
- Return an identical generic response whether or not the account exists (avoid
  user enumeration), and rate-limit requests.
