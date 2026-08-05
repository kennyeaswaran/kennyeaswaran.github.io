#!/usr/bin/env python3
"""
build.py — turns content/*.md into a static website in public/.

    python3 build.py            # build once into public/
    python3 build.py --serve    # build, serve at localhost:8000, rebuild on change

How it works, in four steps:

  1. Read site.yaml for the site title and the navigation menu.
  2. For each file in content/, split off its YAML front matter, expand any
     `<!-- include: ... -->` directives, and convert the Markdown to HTML.
  3. Drop that HTML into templates/base.html (which holds the nav and footer,
     written once and shared by every page).
  4. Write the result to public/, and copy static/ across unchanged.

URL rules:
    content/index.md            ->  public/index.html              (served at /)
    content/publications.md     ->  public/publications/index.html (served at /publications/)
    content/teaching/2026-winter.md
                                ->  public/teaching/2026-winter/index.html

Front matter (the block between --- lines at the top of each .md file):
    title:        page title; also the <h1> unless you set `show_title: false`
    description:  used for the meta description and link previews (optional)
    updated:      a date string shown in the footer (optional)

Dependencies:  pip install pyyaml jinja2 markdown
"""

import argparse
import hashlib
import html as html_lib
import re
import shutil
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
    import markdown
    from jinja2 import Environment, FileSystemLoader
except ImportError as e:
    sys.exit(f"Missing dependency: {e.name}\n  pip install pyyaml jinja2 markdown")

ROOT = Path(__file__).parent.resolve()
CONTENT = ROOT / "content"
GENERATED = ROOT / "generated"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUTPUT = ROOT / "public"

# Matches a whole line like:  <!-- include: generated/publications-list.md -->
# An HTML comment is used so that the raw .md file still previews cleanly in
# any Markdown editor.
INCLUDE_RE = re.compile(r"^[ \t]*<!--[ \t]*include:[ \t]*(\S+?)[ \t]*-->[ \t]*$", re.MULTILINE)

# Used to split a rendered page into its top-level sections.
H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.DOTALL)

MARKDOWN_EXTENSIONS = [
    "attr_list",   # {: .class } annotations on elements
    "def_list",    # definition lists
    "footnotes",
    "md_in_html",  # lets you write Markdown inside a <div markdown="1">
    "sane_lists",
    "smarty",      # straight quotes -> curly quotes, -- -> en dash
    "tables",
]


# ---------------------------------------------------------------------------
# Reading content
# ---------------------------------------------------------------------------

def split_front_matter(text, source):
    """Return (metadata dict, body text) for a file that may start with ---."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        sys.exit(f"{source}: could not parse front matter\n{e}")
    if not isinstance(meta, dict):
        sys.exit(f"{source}: front matter must be a mapping of key: value pairs")
    return meta, parts[2].lstrip("\n")


def expand_includes(text, source, seen=None):
    """Replace `<!-- include: path -->` lines with the contents of that file.

    Paths are relative to the project root, so `generated/publications-list.md`
    means exactly that. Includes may nest; a file may not include itself.
    """
    seen = seen or set()

    def replace(match):
        rel = match.group(1)
        target = (ROOT / rel).resolve()
        if target in seen:
            sys.exit(f"{source}: circular include of {rel}")
        if not target.exists():
            sys.exit(
                f"{source}: include target not found: {rel}\n"
                f"  If this is a generated file, run ./sync-cv.sh first."
            )
        return expand_includes(target.read_text(), rel, seen | {target})

    return INCLUDE_RE.sub(replace, text)


def make_collapsible(html, meta, source):
    """Wrap each `## ` section in a <details> block so it can be folded away.

    Switched on with `collapsible: true` in a page's front matter. Sections are
    open by default — collapsed content is still in the page source, so search
    engines and screen readers see it either way, but a reader arriving at a
    long page should see the content, not a row of shut drawers. List the
    headings that *should* start closed under `collapsed:` (substring match),
    or use `collapsed: all`.

    This uses the browser's own <details> element: no JavaScript, keyboard
    accessible for free, and it degrades to plain visible text in browsers that
    don't support it.

    Note the structural requirement: sections are split at top-level <h2>, so a
    page using this must not wrap its headings inside a container <div> — the
    <details> tags would interleave with it and produce invalid nesting. Pages
    that need list styling should use `body_class:` instead of a wrapper div.
    """
    if not meta.get("collapsible"):
        return html

    closed = meta.get("collapsed") or []
    if isinstance(closed, str):
        closed = "all" if closed == "all" else [closed]

    parts = H2_RE.split(html)          # [preamble, title, body, title, body, ...]
    if len(parts) == 1:
        print(f"    note: {source} sets collapsible but has no '## ' sections")
        return html

    out = [parts[0]]
    for title, body in zip(parts[1::2], parts[2::2]):
        # Unescape entities before matching: a heading like "Texas A&M" reaches
        # us as "Texas A&amp;M", which would never match what's in the yaml.
        plain = html_lib.unescape(re.sub(r"<[^>]+>", "", title)).strip()
        shut = closed == "all" or any(c.lower() in plain.lower() for c in closed)
        out.append(
            f'<details class="section"{"" if shut else " open"}>\n'
            f"<summary><h2>{title}</h2></summary>\n"
            f"{body}</details>\n"
        )
    return "".join(out)


def output_path_for(md_file):
    """Map a content/ Markdown file to (output file, its URL)."""
    rel = md_file.relative_to(CONTENT).with_suffix("")
    if rel.name == "index":
        rel = rel.parent
    if str(rel) == ".":
        return OUTPUT / "index.html", "/"
    return OUTPUT / rel / "index.html", f"/{rel.as_posix()}/"


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------

def asset_version(filename):
    """Short hash of a file in static/, appended to its URL as ?v=...

    Browsers cache stylesheets aggressively, so an edit to style.css can go
    unnoticed for hours behind a stale copy. Changing the URL whenever the
    file's contents change sidesteps that entirely: same file, same URL, so
    caching still works; different file, different URL, so it can't go stale.
    """
    path = STATIC / filename
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def build():
    config = yaml.safe_load((ROOT / "site.yaml").read_text())
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=False)
    template = env.get_template("base.html")
    md = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS)

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    pages = sorted(CONTENT.rglob("*.md"))
    if not pages:
        sys.exit("No Markdown files found in content/")

    for md_file in pages:
        source = md_file.relative_to(ROOT).as_posix()
        meta, body = split_front_matter(md_file.read_text(), source)
        body = expand_includes(body, source)

        md.reset()
        html = make_collapsible(md.convert(body), meta, source)

        out_file, url = output_path_for(md_file)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(template.render(
            site=config,
            page=meta,
            content=html,
            current_url=url,
            build_year=date.today().year,
            css_version=asset_version("style.css"),
        ))
        print(f"  {source:40s} -> {url}")

    write_redirects(config, env)
    copy_static()
    print(f"\nBuilt {len(pages)} pages into {OUTPUT.relative_to(ROOT)}/")


def write_redirects(config, env):
    """Emit tiny HTML pages that bounce old URLs to their new locations."""
    redirects = config.get("redirects") or {}
    if not redirects:
        return
    template = env.get_template("redirect.html")
    for old, new in redirects.items():
        out_file = OUTPUT / old.strip("/") / "index.html"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(template.render(target=new, site=config))
        print(f"  redirect {old:31s} -> {new}")


def copy_static():
    """Copy static/ into the site root, so static/style.css lands at /style.css."""
    if not STATIC.exists():
        return
    for item in STATIC.iterdir():
        dest = OUTPUT / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    print(f"  static/ -> {OUTPUT.name}/")


# ---------------------------------------------------------------------------
# Preview server
# ---------------------------------------------------------------------------

def serve(port=8000):
    """Build, then serve public/ and rebuild whenever a source file changes."""
    import http.server
    import socketserver
    import threading
    import time

    def watched_files():
        for folder in (CONTENT, TEMPLATES, STATIC, GENERATED):
            if folder.exists():
                yield from (p for p in folder.rglob("*") if p.is_file())
        yield ROOT / "site.yaml"

    def snapshot():
        return {p: p.stat().st_mtime for p in watched_files()}

    def watch():
        last = snapshot()
        while True:
            time.sleep(0.5)
            current = snapshot()
            if current != last:
                last = current
                print("\nChange detected, rebuilding...")
                try:
                    build()
                except SystemExit as e:
                    print(f"Build failed: {e}")

    build()
    threading.Thread(target=watch, daemon=True).start()

    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(OUTPUT), **kw)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\nPreview at http://localhost:{port}/   (Ctrl-C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--serve", action="store_true",
                        help="serve the site locally and rebuild on every save")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    serve(args.port) if args.serve else build()
