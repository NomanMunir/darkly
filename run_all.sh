#!/usr/bin/env bash
cd "$(dirname "$0")"

for d in 00-Recon 01-Weak-Password-BruteForce 02-Broken-Password-Reset \
         03-IDOR-Profile 04-PrivEsc-Mass-Assignment 05-JWT-Forgery \
         06-XXE-SSRF 07-PocketBase-Admin 08-Stored-XSS 09-Reflected-XSS \
         10-Broken-Access-Grades 11-Open-Redirect 12-Unrestricted-File-Upload; do
  echo
  echo "==================== $d ===================="
  bash "$d/exploit.sh"
done
