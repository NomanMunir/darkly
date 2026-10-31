# Darkly v2 — my walkthrough (plain words)

This is the story of how I broke into the Darkly website, step by step, in the
order I actually did it. The site has two parts: the pages you see
(`http://localhost:4942`) and the database behind them (`http://localhost:8090`).
My goal was to find the hidden flags (secret codes that look like `FLAG{...}`).

Each step below has its own folder with a tiny script (`exploit.sh`) that does
exactly what I describe, and a longer note (`explanation.md`) if you want the
deeper "why". You can run everything at once with `./run_all.sh`.

I found **7 flags**. Here is how.

---

## Step 0 — Just looking around (folder `00-Recon`)
Before touching anything I just read the site like a nosy visitor.

- The page headers tell me it's built with FastAPI and that the database is at
  `localhost:8090`. Free information.
- `robots.txt` is supposed to hide pages from Google, but it basically gives me a
  map of the secret pages (`/admin`, `/staff`, `/backup`, `/_/`, ...).
- The page source (right-click → view source) is full of developers arguing in
  comments, leaking almost every weakness.
- A forum post hides a line of base64 text. I decode it and it says
  `validation_key=42network`.

Nothing secret yet, but now I know where everything is.

## Step 1 — The weak password → **FLAG 1** (folder `01-Weak-Password-BruteForce`)
On the forum, a student called **jdoe** brags that he never changed his sign-up
password, and people reply "it's near the top of the most famous list." That's a
dare. I try the most common passwords at the login box, and **`abc123`** works.

Now I'm logged in as jdoe. I open my grades page and there's the first flag:
`FLAG{md5_1s_4_n4m3pl4t3_n0t_4_l0ck}`.

(The site also shows a "password hint" that is just the md5 of the password, so I
could also crack it on my own computer instead of guessing at the login — same
result. More on that in the folder's note.)

## Step 2 — The broken "forgot password" → **FLAG 2** (folder `02-Broken-Password-Reset`)
I try the "forgot password" link for another student, **benjamin**. Instead of
emailing him a reset link, the server hands the reset token straight back to me
in the URL. Worse, that token is just the md5 of his email address — so I never
even needed to ask.

I use it to set benjamin's password to whatever I want, log in as him, and his
settings page shows his recovery code, which is the flag:
`FLAG{r3s3t_t0k3n_w4s_just_md5_lol}`.

## Step 3 — Reading other people's profiles → **FLAG 3** (folder `03-IDOR-Profile`)
The site gave me a list of all users and their ids. Profiles are supposed to be
private, but if I just put someone else's id in the profile URL, it shows me
their private stuff anyway. **wil**'s profile has a private note with a flag:
`FLAG{1d0r_ur_pr0f1l3_1s_m1n3}`.

## Step 4 — Promoting myself → **FLAG 4** (folder `04-PrivEsc-Mass-Assignment`)
jdoe is only a "student". When I edit my profile, the request also lets me set my
own **role**. So I set myself to **cadet**. I log in again so the new role sticks,
and now the staff dashboard opens for me, with a flag:
`FLAG{just_p4tch_y0ur_0wn_r0l3_lol}`.

It won't let me jump straight to "staff" or "god" this way — that needs Step 5.

## Step 5 — Faking the admin's login cookie (folder `05-JWT-Forgery`)
The site accidentally told me the secret password it uses to sign login cookies:
**`42network`**. With that secret I can make my own cookie that says I'm anyone.
I make one for the admin **sophie**, and the admin page opens for me — no password
needed. (This step is the key that unlocks admin; the flag it leads to is in the
next steps.)

## Step 6 — Tricking the server into reading its own secrets → **FLAG 5** (folder `06-XXE-SSRF`)
The agenda page lets me upload an XML file and trusts it far too much. I write an
XML file that secretly says "server, go fetch your own secret config page and put
it here." That config page is normally blocked — unless the request comes from the
server itself, which is exactly what my trick does.

It works, and the secret page is printed back to me. It contains a flag:
`FLAG{d3fus3dxml_n3xt_spr1nt_pr0m1s3}` — plus the database admin login.

## Step 7 — Taking over the database → **FLAG 6** (folder `07-PocketBase-Admin`)
That secret page handed me the database admin login
(`admin@42network.local` / `Darkly42Admin!`). The database is reachable on port
8090, so I log straight into it as admin. Now I can read every table. One of them,
`internal_audit`, holds a flag: `FLAG{th3_und3rsc0r3_sl4sh_kn0ws_th3_w4y}`.

## Step 8 — Making a robot steal a cookie for me → **FLAG 7** (folder `08-Stored-XSS`)
A moderation robot opens every new forum post in a real browser, and that robot
carries a secret cookie. Forum posts allow raw HTML, so I post a message with a
hidden script that says "whoever opens this, send me your cookies." I start a tiny
server to catch the result, wait about a minute, and the robot sends me its cookie
— which contains the flag: `FLAG{xss_st0r3d_1s_n0t_4_f34tur3_w1l}`.

---

## The ladder (how the "levels" connect)
The site has ranks: visitor → student → cadet → staff → god (admin).
- I become a **student** by guessing jdoe's password (Step 1).
- I become a **cadet** by editing my own role (Step 4).
- I become the **admin** by faking the cookie with the leaked secret (Step 5),
  which I got for free from the XML trick (Step 6).
- I take over the whole **database** last (Step 7).

## A few more weaknesses (no flag, but worth showing)
- **09-Reflected-XSS** — the newsletter prints my email back as raw HTML, so a
  crafted link could run a script in a victim's browser.
- **10-Broken-Access-Grades** — the grades page shows me anyone's grades, and a
  trick value dumps everyone's at once.
- **11-Open-Redirect** — a `/redirect` link will forward a victim to any website,
  great for phishing.
- **12-Unrestricted-File-Upload** — the upload only checks the file type in the
  browser, so I can send any kind of file.

## How to run it
Boot the VM, make sure `http://localhost:4942` answers, then:
```bash
./run_all.sh
```
or run any single step, e.g. `bash 01-Weak-Password-BruteForce/exploit.sh`.

## One honest note
The site claims 10 flags. I found 7 using only the website (no cheating by
opening the virtual machine). The other 3 are hidden deeper in the app's code
behind triggers I couldn't reach from the outside; they're noted as open leads
rather than guessed.
