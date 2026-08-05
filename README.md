# kennyeaswaran.org

The source for my website. Pages are Markdown files in `content/`; a small
Python script turns them into HTML.

## One-time setup

```
pip install -r requirements.txt
```

## Editing

Everything you'd normally want to change is a `.md` file in `content/`:

| Page | File |
| --- | --- |
| Home | `content/index.md` |
| Publications | `content/publications.md` |
| Teaching | `content/teaching.md` |
| CV | `content/cv.md` (mostly generated — see below) |
| AI seminar | `content/teaching/2026-ai-seminar.md` |

To see your changes:

```
python3 build.py --serve
```

Then open <http://localhost:8000>. Leave it running — every time you save a
file, the site rebuilds and you can just refresh the browser. Ctrl-C to stop.

### Markdown reminders

```markdown
*italic*        **bold**        [link text](https://example.com)

## A section heading
### A smaller heading

- a list item
- another one
```

A blank line is required before a list and between paragraphs.

### Adding a page

Create a file, e.g. `content/teaching/2026-fall-seminar.md`, starting with:

```markdown
---
title: "LPS 999: Seminar Title"
description: "One sentence, used for Google results and link previews."
---

Your text here.
```

It will appear at `/teaching/2026-fall-seminar/`. To add it to the menu at the
top of every page, add an entry to `nav` in `site.yaml`.

### Publication and course lists

These use a wrapper so the list gets the right styling:

```markdown
<div class="bib" markdown="1">

- Author. "Title". *Journal* 12:3 (2025), 1–20. [(journal)](https://…){: .alt }

</div>
```

`{: .alt }` makes a link small and grey — used for the secondary
"(journal)" and "(publisher)" links.

## Updating the CV

The CV page and the downloadable PDF both come from the CV project in
`../CV and AP-10`. After you change something there:

```
./sync-cv.sh
```

That regenerates `generated/cv-body.md` and `static/easwaran-cv.pdf`. Nothing
in this repository ever writes back to the CV project.

## Publishing

```
git add -A
git commit -m "describe what changed"
git push
```

GitHub Actions builds and deploys automatically — usually live within a minute.
If something goes wrong, the repository's **Actions** tab shows the error.

## Switching the domain over (not yet done)

Until `kennyeaswaran.org` is pointed at GitHub, the site lives at
`https://<username>.github.io/<repo>/`.

`CNAME.disabled` in this folder is the file that claims the custom domain. It
is deliberately *outside* `static/`, so it is not published. Publishing it
early would make GitHub redirect the github.io address to
`www.kennyeaswaran.org`, which still points at Google Sites — so the preview
would appear to show the old site.

When the DNS records are in place, move it into `static/` and push:

```
mv CNAME.disabled static/CNAME
```
