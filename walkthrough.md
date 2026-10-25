# Darkly v2 — Audit Walkthrough

A security audit of the **Darkly v2** web platform (42 Network clone):
Ubuntu 24.04 + **FastAPI** (uvicorn) front end on `:4942`, **PocketBase** backend
on `:8090`.

> **Lab setup.** The sealed appliance ships as `Darkly_v2.ova`. It is booted in a
> hypervisor (VirtualBox, or QEMU/KVM as used here) with NAT port-forwards
> `4942→4942`, `8090→8090`. All testing targets the web app at
> `http://localhost:4942` (and its backend `http://localhost:8090`) — the VM OS
> itself was never touched. Scripts assume a **pristine** appliance.
>
> Several exploits exfiltrate via an out-of-band listener; the guest reaches the
> host at **`10.0.2.2`** under NAT. Start `tools/oob_listener.py 9900 /tmp/log`
> first for Breach 08 (the script does this automatically).

## Target profile
| Thing | Value |
|---|---|
| Front end | FastAPI 0.104 / uvicorn (`:4942`) |
| Backend | PocketBase 0.22.4 (`:8090`, admin UI at `/_/`) |
| Session | HS256 JWT in `session` cookie, secret **`42network`**, **not HttpOnly** |
| Roles (low→high) | `visitor → student → cadet → staff → god` |
| Admin | `sophie` (role `god`, id `enplwhu8jfo56oi`) |
| Tutorial account | `jdoe` / `abc123` (`jdoe@student.42.tech`) |

## Flags recovered (7)

| # | Flag | Breach (folder) |
|---|------|-----------------|
| 1 | `FLAG{md5_1s_4_n4m3pl4t3_n0t_4_l0ck}` | 01 — Weak password / brute force |
| 2 | `FLAG{r3s3t_t0k3n_w4s_just_md5_lol}` | 02 — Broken password reset |
| 3 | `FLAG{1d0r_ur_pr0f1l3_1s_m1n3}` | 03 — IDOR on profiles |
| 4 | `FLAG{just_p4tch_y0ur_0wn_r0l3_lol}` | 04 — Mass-assignment privesc |
| 5 | `FLAG{d3fus3dxml_n3xt_spr1nt_pr0m1s3}` | 06 — XXE → SSRF |
| 6 | `FLAG{th3_und3rsc0r3_sl4sh_kn0ws_th3_w4y}` | 07 — PocketBase superuser |
| 7 | `FLAG{xss_st0r3d_1s_n0t_4_f34tur3_w1l}` | 08 — Stored XSS (bot cookie) |

This satisfies the **mandatory** part (6 flags; here 7) and the 4-level
privilege-escalation chain, plus more than the 10 required vulnerabilities.

### The privilege-escalation chain (4 gates)
```
visitor ──(01 brute force jdoe:abc123)──▶ student     → flag md5_1s (own grade)
student ──(04 PATCH /api/profile role)──▶ cadet       → flag just_p4tch
cadet   ──(06 XXE leaks jwt_secret ; 05 forge JWT)──▶ admin (sophie/god) → /admin
admin   ──(06 leaks PB creds ; 07 PocketBase /_/)──▶ backend superuser   → flag th3_und3rsc0r3
```
The two **"flags of choice"** used are **03 (IDOR)** and **02 (broken reset)**;
**08 (stored XSS)** is a bonus flag.

## Vulnerabilities explained (16)
Flag-bearing: **01** weak password/brute force · **02** broken password reset ·
**03** profile IDOR · **04** mass-assignment privesc · **06** XXE→SSRF ·
**07** PocketBase superuser exposure · **08** stored XSS.
No-flag: **00** info disclosure (debug headers, HTML comments, `robots.txt`,
`/api/docs-internal`, base64 `validation_key`, `/backup` debug headers,
`pw_hint` table) · **05** JWT forgery w/ leaked secret · **09** reflected XSS ·
**10** broken access control + filter injection on `/api/grades` ·
**11** open redirect · **12** unrestricted file upload · plus the **missing
`HttpOnly`** session-cookie flag (covered under 05/08).

Each `NN-*/explanation.md` covers *how it works, impact, and remediation*; each
`NN-*/exploit.sh` reproduces it and writes the recovered token to `NN-*/flag`.

## How to run
```bash
# boot the appliance (VirtualBox import, or QEMU), confirm http://localhost:4942
./run_all.sh                     # runs every breach, prints each flag
# or individually:
BASE=http://localhost:4942 ./01-Weak-Password-BruteForce/exploit.sh
```

## Status note (bonus)
The platform advertises **10** flags. **7** were recovered through pure web
exploitation (above). The remaining **3** are generated inside the FastAPI
application behind trigger conditions that did not surface during an extensive
black-box audit (every endpoint fuzzed; PocketBase DB + full backup dumped; XXE
HTTP-SSRF; moderation-bot abuse; reflected XSS; `/api/grades` filter injection;
open redirect; LFI attempts on `/projects/download`; base64 `validation_key` →
`/backup` metadata → `data/private_notes.txt`; localhost port scan via SSRF).
They are documented here as open leads rather than guessed.
