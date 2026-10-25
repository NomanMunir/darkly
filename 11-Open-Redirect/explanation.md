# Breach 11 — Open redirect

**Flag:** none (vulnerability without a flag).
**Type:** OWASP A01 — Broken Access Control (Unvalidated Redirect)

## How it works
`/redirect?next=<url>` issues a `307` to whatever `next` contains, with no
allow-list — including external origins (`https://evil.example.com`),
scheme-relative (`//evil.example.com`) and even `javascript:` URLs. The footer
and the Google login button route through it
(`/redirect?next=https://accounts.google.com`), so links look trustworthy.

## Impact
Phishing (a `42.tech` link that lands on an attacker site), and theft of
tokens/codes appended to a legitimate-looking redirect (e.g. OAuth flows).

## Remediation
- Redirect only to a server-side allow-list of known paths/hosts, or to
  relative paths you control; reject absolute/scheme-relative/`javascript:` URLs.
- If an external redirect is unavoidable, show an interstitial warning.
