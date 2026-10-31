#!/usr/bin/env python3
import sys, hmac, hashlib, base64, json, time

def b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

sub, login, role = sys.argv[1], sys.argv[2], sys.argv[3]
secret = b"42network"

header = {"alg": "HS256", "typ": "JWT"}
payload = {"sub": sub, "login": login, "role": role, "exp": int(time.time()) + 86400}

part1 = b64(json.dumps(header).encode())
part2 = b64(json.dumps(payload).encode())
sig = b64(hmac.new(secret, (part1 + "." + part2).encode(), hashlib.sha256).digest())

print(part1 + "." + part2 + "." + sig)
