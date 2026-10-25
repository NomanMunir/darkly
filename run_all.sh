#!/usr/bin/env bash
# Run every breach exploit against a pristine appliance and summarise the flags.
# Usage: BASE=http://localhost:4942 PB=http://localhost:8090 ./run_all.sh
set -uo pipefail
export BASE="${BASE:-http://localhost:4942}"
export PB="${PB:-http://localhost:8090}"
HERE="$(cd "$(dirname "$0")" && pwd)"
echo "=== Darkly audit — running all breaches against $BASE ==="
for d in 00-Recon 01-Weak-Password-BruteForce 02-Broken-Password-Reset \
         03-IDOR-Profile 04-PrivEsc-Mass-Assignment 05-JWT-Forgery \
         06-XXE-SSRF 07-PocketBase-Admin 08-Stored-XSS 09-Reflected-XSS \
         10-Broken-Access-Grades 11-Open-Redirect 12-Unrestricted-File-Upload; do
  echo; echo "########## $d ##########"
  bash "$HERE/$d/exploit.sh" || echo "[-] $d exited non-zero"
done
echo; echo "=== Flags collected ==="
for f in "$HERE"/*/flag; do [ -f "$f" ] && printf '%-34s %s\n' "$(basename "$(dirname "$f")")" "$(cat "$f")"; done
