#!/usr/bin/env python3
"""
Render the repo's Markdown write-ups into styled, standalone HTML pages under
docs/. The Markdown files stay the source of truth; re-run this to regenerate:

    python3 docs/build.py

It converts the small Markdown subset used in this repo (headings, bold, inline
and fenced code, bullet lists, blockquotes, GitHub tables, links) — no external
dependencies, output works offline via file://.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Which pages to build: (source .md, output .html, nav title)
PAGES = [("walkthrough.md", "index.html", "Overview")]
for d in sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"\d\d-", p.name)):
    md = d / "explanation.md"
    if md.exists():
        PAGES.append((md.relative_to(ROOT).as_posix(), f"{d.name}.html", d.name))


def inline(text: str) -> str:
    """Escape, then apply inline Markdown (code, bold, links)."""
    # pull out `code` spans first so their contents aren't escaped twice / bolded
    spans: list[str] = []

    def stash(m):
        spans.append(m.group(1))
        return f"\x00{len(spans)-1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\x00(\d+)\x00",
                  lambda m: f"<code>{html.escape(spans[int(m.group(1))])}</code>", text)
    return text


def md_to_html(md: str) -> str:
    out: list[str] = []
    lines = md.splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]

        # fenced code block
        if line.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1  # closing fence
            out.append('<pre class="code"><code>'
                       + html.escape("\n".join(buf)) + "</code></pre>")
            continue

        # table (consecutive lines starting with |)
        if line.lstrip().startswith("|"):
            tbl = []
            while i < n and lines[i].lstrip().startswith("|"):
                tbl.append(lines[i]); i += 1
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl]
            rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
            if rows:
                out.append("<table>")
                out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead>")
                out.append("<tbody>")
                for r in rows[1:]:
                    out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
                out.append("</tbody></table>")
            continue

        # headings
        m = re.match(r"(#{1,6})\s+(.*)", line)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        # blockquote
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i][1:].lstrip()); i += 1
            out.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>")
            continue

        # unordered list
        if re.match(r"\s*[-*]\s+", line):
            out.append("<ul>")
            while i < n and re.match(r"\s*[-*]\s+", lines[i]):
                item = re.sub(r"^\s*[-*]\s+", "", lines[i])
                out.append(f"<li>{inline(item)}</li>"); i += 1
            out.append("</ul>")
            continue

        # blank line
        if not line.strip():
            i += 1
            continue

        # paragraph (gather until blank / block starter)
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(
                r"(#{1,6}\s|```|>|\s*[-*]\s|\|)", lines[i]):
            buf.append(lines[i]); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out)


def nav(active: str) -> str:
    items = []
    for _src, out_html, title in PAGES:
        cls = ' class="active"' if out_html == active else ""
        label = "Overview" if out_html == "index.html" else title
        items.append(f'<a href="{out_html}"{cls}>{html.escape(label)}</a>')
    return '<nav class="side">' + "\n".join(items) + "</nav>"


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Darkly v2 audit</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="layout">
{nav}
<main class="content">
<div class="crumb">Darkly v2 — security audit</div>
{body}
<footer>Generated from {src} · do not edit the HTML by hand — run <code>python3 docs/build.py</code></footer>
</main>
</div>
</body>
</html>
"""


def main():
    DOCS.mkdir(exist_ok=True)
    for src, out_html, title in PAGES:
        md = (ROOT / src).read_text(encoding="utf-8")
        body = md_to_html(md)
        page = TEMPLATE.format(title=html.escape(title), nav=nav(out_html),
                               body=body, src=html.escape(src))
        (DOCS / out_html).write_text(page, encoding="utf-8")
        print(f"[+] {src} -> docs/{out_html}")


if __name__ == "__main__":
    main()
