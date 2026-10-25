# Breach 12 — Unrestricted file upload (no server-side validation)

**Flag:** none (vulnerability without a flag).
**Type:** OWASP A04 — Insecure Design / A05 — Security Misconfiguration

## How it works
The agenda importer's `<input type="file" accept=".xml">` restriction is
client-side only. The server checks neither the extension nor the content-type
before handing the bytes to the XML parser — deploy log: *"quick fix on file
upload (removed the whitelist entirely)."* Files named `*.php` or sent with an
arbitrary MIME type are accepted and processed.

On its own this is a missing-validation finding; combined with the entity-
expanding parser it is the delivery vector for the XXE/SSRF in Breach 06.

## Impact
Removing upload validation widens the attack surface (parser abuse / XXE here;
on a differently-configured deployment it enables webshell or content-type
confusion attacks).

## Remediation
- Validate uploads server-side: allow-list extensions **and** sniff/enforce the
  real content type; cap size; store outside the web root with non-executable
  perms and randomised names.
- Parse XML with a hardened parser (see Breach 06).
