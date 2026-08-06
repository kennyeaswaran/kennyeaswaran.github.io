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

## Course pages

Each course gets a page at `/teaching/<year><term>/<course>/`, where term is
`W`, `S`, `Su`, or `F` and course is the department abbreviation plus the
undergraduate number — so `content/teaching/2026F/lps105a.md` serves at
`/teaching/2026F/lps105a/`. Give each term folder an `index.md` too, so that
someone trimming the URL back to `/teaching/2026F/` doesn't hit a 404.

Files that belong to a course — handouts, slides, notes — go in the matching
folder under `static/`:

```
content/teaching/2026F/lps105a.md                     the page
static/teaching/2026F/lps105a/set-theory-notes.pdf    a file it links to
```

### Revising notes during a term

**Keep one filename and overwrite it.** Don't post `notes-oct-6.pdf`,
`notes-oct-20.pdf` and so on the way the old site did — that was a workaround
for Google Sites having no version history. Git keeps every version you commit,
so nothing is lost, and students always get the current file from a link that
never changes.

Put the date in the link text and edit that line when you update:

```markdown
[Class notes (PDF, updated 6 October 2026)](/teaching/2026F/lps105a/set-theory-notes.pdf){: .button }
```

(It isn't automatic because git doesn't preserve file modification times, so an
auto-generated date would show when the site was last deployed, not when you
last revised the notes.)

After pushing, allow up to ten minutes before the new PDF appears — that's
GitHub's cache, not a failed deploy.

### Old course pages are records, not rewrites

Pages migrated from the old site keep their original wording — including the
tense. A syllabus that said "you will write five papers" still says that; it
isn't rephrased into the past. Institutional boilerplate stays, and so do the
struck-through mid-term edits, because they're part of what the page was. The
page should look preserved, not retold.

The only things removed are ones that are unsafe or meaningless rather than
merely old — live meeting links, which are marked *(Zoom link removed)* where
they stood so the gap is visible, and student names in schedules.

### Readings by other people

Host your own work; link out for everyone else's. When a syllabus cites a book
chapter or article that isn't yours, give the citation and no link — don't put
a scan on the site. A PDF shared privately with a class is one thing; the same
file served from kennyeaswaran.org is another. Anyone reading an old syllabus
can find their own copy.

## Updating the CV

**The short version — three commands from this folder:**

```
./sync-cv.sh
git add -A && git commit -m "Update CV" && git push
```

That's the whole routine. You never edit the CV page's contents by hand.

**What's actually happening.** The facts live in the CV project
(`../CV and AP-10/data/*.yaml`) — one file per category, so a new editorship
goes in `service.yaml`, a new student in `supervision.yaml`, and so on. Edit
the fact there, then run `./sync-cv.sh` here. It regenerates three things:

| File | What it feeds |
| --- | --- |
| `generated/cv-body.md` | the body of the **CV page** |
| `generated/publications-list.md` | the generated part of the **Publications page** |
| `static/easwaran-cv.pdf` | the **full CV PDF** the page links to |

Those files are committed to git, which is why GitHub never needs access to the
CV project. Push, and the site rebuilds itself.

The flow is strictly one-way: nothing here ever writes back into the CV project.

**Changing *which* sections appear.** The CV page is deliberately shorter than
the PDF — it skips honors, grants, talks, publications and general service, and
trims editorships to current ones and conference organization to leadership
roles. All of that is decided by `profiles/web-cv.yaml` in the CV project, which
is a plain list of sections with filters. To add a section back, uncomment or
copy one; to narrow one, add a filter such as `current_only: true` or
`lead_only: true`. No code changes needed — the profile is the control panel.

Note that `./sync-cv.sh` needs `typst` installed to rebuild the PDF. If it
prints `PDF skipped`, the Markdown still updates correctly but
`static/easwaran-cv.pdf` will be whatever was last built — so check that file
isn't accidentally reverted before committing.

## Publishing

```
git add -A
git commit -m "describe what changed"
git push
```

GitHub Actions builds and deploys automatically — usually live within a minute.
If something goes wrong, the repository's **Actions** tab shows the error.

## The custom domain

`www.kennyeaswaran.org` points at GitHub Pages via four `A` records on the apex
and a `CNAME` on `www` (set at Squarespace Domains, where the domain is
registered). The domain itself is claimed in the repository's
**Settings → Pages**, *not* by a file in this repo — because publishing goes
through a GitHub Actions workflow, GitHub ignores any `CNAME` file in the built
output. Don't add one to `static/`.
