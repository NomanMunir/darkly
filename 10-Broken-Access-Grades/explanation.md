# Breach 10 — Broken access control + filter injection on `/api/grades`

**Flag:** none (vulnerability without a flag — though it discloses jdoe's grade
flag `md5_1s_...` to anyone).
**Type:** OWASP A01 — Broken Access Control / A03 — Injection (NoSQL/filter)

## How it works
`/api/grades?student=<id>` has two defects:

1. **IDOR / missing authorization.** It never checks that `<id>` is the
   authenticated caller, so any logged-in user can read anyone's grades (the
   endpoint is even "protected" only by `robots.txt: Disallow: /api/grades`).

2. **Filter injection.** The `student` value is concatenated into a PocketBase
   filter string (effectively `student="<id>"`). Injecting
   `x" || id!="` makes the filter `student="x" || id!=""` — always true —
   returning **every grade row of every student** (26 rows vs. the caller's 6).

## Impact
Disclosure of all students' evaluation data; the injection is a generic
filter-logic bypass that could be extended to other filtered queries.

## Remediation
- Enforce that `student` equals the authenticated user (or require staff role).
- Never build filters by string concatenation — use parameterised filters/bound
  values (PocketBase supports `filter` with typed params).
- Remove reliance on `robots.txt` as an access control.
