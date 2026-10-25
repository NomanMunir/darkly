# Breach 09 — Reflected XSS (newsletter banner)

**Flag:** none (vulnerability without a flag).
**Type:** OWASP A03 — Injection (Cross-Site Scripting, reflected)

## How it works
Subscribing to the newsletter redirects to
`/newsletter?email=<value>&msg=subscribed`, and the page echoes the email into a
success banner **without HTML-encoding**:
```html
<div class="alert alert-success">You're now subscribed with: <img src=x onerror=alert(document.domain)></div>
```
`<script>`, `<svg onload>` and `<img onerror>` all execute. The source comments
confirm it: *"the 'subscribed with: ___' banner echoes your email straight back
… unescaped?? … define 'unescaped'"* and *"someone subscribed with a `<script>`
tag last week … it worked."*

A crafted link (`/newsletter?email=<payload>&msg=subscribed`) sent to a victim
runs attacker JS in their session.

## Impact
Reflected XSS: session/credential theft, request forgery, UI redressing against
any user who follows a crafted link.

## Remediation
- HTML-encode all reflected values (template auto-escaping), and validate that
  `email` is actually an email.
- Add a strict `Content-Security-Policy`; set `HttpOnly` on session cookies.
