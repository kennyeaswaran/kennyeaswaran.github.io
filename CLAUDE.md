# kennyeaswaran.org — operating guide

A hand-edited static site. Markdown content plus a ~150-line Python build
script; no framework. Deployed to GitHub Pages, served at
`https://www.kennyeaswaran.org`.

This project *reads from* the CV project (`../CV and AP-10`) but never writes
to it. That one-way flow is the whole integration: keep it that way.

## Layout

```
.
├── CLAUDE.md  README.md                # docs
├── build.py                            # Markdown + Jinja2 -> HTML
├── sync-cv.sh                          # pulls generated CV out of the CV project
├── site.yaml                           # site title, nav, redirects
├── content/                            # the pages (hand-written Markdown)
│   ├── index.md  publications.md  teaching.md  cv.md
│   └── teaching/2026-ai-seminar.md
├── generated/                          # written by sync-cv.sh; committed
│   └── cv-body.md
├── templates/base.html  redirect.html  # shared page chrome
├── static/                             # copied verbatim to the site root
│   ├── style.css  easwaran-cv.pdf
│   ├── papers/                         # publications (see below)
│   ├── teaching/                       # course materials (see below)
│   └── images/                         # home-page photos
└── public/                             # build output (gitignored)
```

## Commands

```
pip install -r requirements.txt     # once
python3 build.py                    # build into public/
python3 build.py --serve            # preview at localhost:8000, rebuilds on save
./sync-cv.sh                        # refresh cv-body.md and the CV PDF
```

Deployment is automatic: pushing to `main` triggers
`.github/workflows/deploy.yml`, which builds and publishes. Nothing is deployed
from a local machine.

**The custom domain is set in the repository's Settings → Pages, not in a file.**
Because publishing goes through a GitHub Actions workflow rather than a branch,
GitHub ignores any `CNAME` file in the built output — so don't add one to
`static/`. (A `CNAME.disabled` stub lived at the repo root until August 2026,
left over from an earlier plan; it was removed once this was confirmed.)

## How the pieces fit

**Navigation** lives only in `site.yaml`. `templates/base.html` renders it on
every page and marks the current one via `aria-current`. Never hard-code a nav
menu into a page.

**Adding a page** means adding a Markdown file under `content/`. The output URL
is derived from the path: `content/foo.md` → `/foo/`,
`content/teaching/bar.md` → `/teaching/bar/`. Add it to `site.yaml`'s `nav`
only if it belongs in the top-level menu.

**Front matter** (the `---` block at the top of each page) takes `title`,
`description`, `updated`, and `show_title: false` for pages that supply their
own heading.

**Includes.** A line of the form `<!-- include: generated/cv-body.md -->` is
replaced with that file's contents before Markdown conversion. Paths are
relative to the project root. This is how generated CV content reaches
`content/cv.md` while keeping the page itself hand-editable.

**Redirects.** `site.yaml`'s `redirects` map emits meta-refresh stubs so old
Google Sites URLs keep working. Add an entry whenever a page moves.

**Where PDFs live.** The split is by kind of thing, not by convenience:

- `static/papers/` — publications only, plus the few items that are
  structurally the same sort of object: the dissertation, the *Cheerful
  Introduction to Forcing*, the note revisiting *Why Countable Additivity?*,
  and the *Cities after COVID* essay. Filenames match the publication `id` in
  the CV store, which is what `pdf:` fields point at.
- `static/teaching/` — course materials. Files for a specific course sit beside
  that course's page (`static/teaching/2025F/lps105a/set-theory-notes.pdf`
  serves at `/teaching/2025F/lps105a/set-theory-notes.pdf`); material not tied
  to one course sits at the top (`static/teaching/godels-theorem.pdf`).

`copy_static` merges directories rather than replacing them, which is what lets
`static/teaching/2025F/…` coexist with the pages `content/teaching/2025F/…`
generates.

**Readings on course pages.** Kenny's own material is hosted here. Scans and
PDFs of other people's work are *not* — when migrating an old syllabus, drop
the link and keep the citation. Someone reading a syllabus from 2011 can find
their own copy, and a link that was fine as Dropbox sharing with a class is a
different proposition served from kennyeaswaran.org.

**Migrated course pages are museum records.** Keep the original wording,
including tense: a syllabus that said "you will write five papers" still says
that, rather than being rewritten into the past. Keep institutional boilerplate
(Title IX, disability statements) and the struck-through edits made mid-term —
they are part of what the page was. The page should read as a preserved
artefact, not as a summary written years later.

The exceptions are things that are unsafe or useless rather than merely old:
live meeting links are removed and marked *(Zoom link removed)* in place, so
the deletion is visible; `google.com/url?q=…` redirect wrappers are decoded to
the URL underneath; and student names are dropped from schedules.

**Revising course notes mid-term.** Keep one stable filename
(`set-theory-notes.pdf`) and overwrite it on each revision, rather than adding
a dated file per version as the Google Sites page did. The link never changes,
students always land on the current version, and git holds every prior revision
if one is ever needed. Put the date in the link *text* so readers can see how
current it is.

**Course pages** live at `/teaching/<YYYY><term>/<course>/`, where term is
`W`, `S`, `Su`, or `F`, and course is the department abbreviation plus the
primary (undergraduate) number, lowercase and unpunctuated: `lps105a`,
`phil485`, `arlt100g`. Each term directory gets an `index.md` so that trimming
a URL back to the term doesn't 404. Every migrated page needs a `redirects`
entry for its old Google Sites path, and a `page:` field on the matching record
in the CV project's `data/teaching.yaml`.

## Styling conventions

All CSS is in `static/style.css`; the variables in `:root` (measure, colours,
fonts) are the intended adjustment points. Three content classes matter:

- `.bib` — bibliography lists with hanging indents (publications, media)
- `.terms` — term-and-course lists on the Teaching page
- `.contact` — the small contact block on the home page
- `.photo right` / `.photo left` — a single portrait floated beside a section
  of text; `main h2 { clear: both }` is what keeps consecutive sections from
  colliding, so each floated photo belongs to exactly one section
- `.photo-stack right` / `.photo-stack left` — a `<div>` wrapping two or more
  photos stacked down one side. The *wrapper* floats: floating the images
  individually would let them sit side by side whenever the column was wide
  enough. Becomes a side-by-side pair on narrow screens.
- `.photo-row` — a flex row of square-cropped photos (used at the foot of the
  home page). Markdown wraps the images in a `<p>`, which
  `.photo-row p { display: contents }` neutralises.
- `figure.photo-figure` — a full-measure photo with a caption beneath, for
  pictures whose caption carries information (who, when, where) rather than
  decoration. Written as literal `<figure>`/`<figcaption>`, not Markdown.

Home-page photos live in `static/images/`, named `YYYY-MM-description.jpg` and
placed newest-first down the page. They are re-encoded on import, which strips
EXIF (including GPS coordinates from phone photos).

**These must be applied with a wrapper, not a trailing `{: .class }`:**

```markdown
<div class="bib" markdown="1">

- First entry
- Second entry

</div>
```

Python-Markdown's `attr_list` attaches a trailing `{: .class }` to the last
*list item*, not the list, so the wrapper form is required for any list-level
class. `{: .class }` is still correct for paragraphs (`.lede`, `.note`) and for
inline links (`.alt`, `.button`).

## Relationship to the CV project

`sync-cv.sh` runs `generate_cv.py` over `profiles/web-cv.yaml` in the CV
project, strips the generator's title block (everything before the first `## `
line, since the website supplies its own heading), and writes
`generated/cv-body.md`. It also copies `build/complete-cv.pdf` to
`static/easwaran-cv.pdf`.

`profiles/web-cv.yaml` lives in the CV project and is deliberately shorter than
the PDF: it omits publications and talks (both have better homes elsewhere),
honors, grants, and general service, and narrows editorships to current ones
(`current_only: true`) and conference organization to leadership roles
(`lead_only: true`).

A section may also carry `group:`, which emits a shared level-1 heading with
each grouped section below it as a level-2 subheading. The three supervision
sections use this, so the website renders them as one collapsible "Graduate
Supervision" block with three subsections rather than three separate blocks —
`make_collapsible` splits on `<h2>` only, so `<h3>`s stay inside their
section.

Generated output is committed so that GitHub Actions never needs access to the
CV project.

The Publications page is generated the same way, from
`profiles/web-publications.yaml`. That profile sets `link_titles: true` so each
title links to the `pdf:` field on its record (a path under `/papers/`), with
the publisher/DOI `url` as a small trailing "(journal)" link. `sync-cv.sh`
writes the result to `generated/publications-list.md`, which `content/
publications.md` includes; the hand-written Media, Work in progress, and
Dissertation sections live in that page directly.

**Not yet wired up:** the Teaching index is still hand-maintained. Every course
record in `data/teaching.yaml` that has a migrated page now carries a `page:`
field, so generating the index is possible — but it needs a `group_by: term`
feature in `generate_cv.py` to keep the term-grouped layout the page uses.

## Provenance

Built August 2026, migrating content from the Google Sites version of
kennyeaswaran.org. Stale facts corrected during migration: the rank at UC
Irvine (Professor, not Associate Professor), leftover Texas A&M links on the
home page, and a Texas A&M link for Matthew Sheldon's UCI affiliation.

All 33 course pages that existed on the Google Site were migrated (UCI 2, Texas
A&M 16, USC 15 including the Phil 285 paper-topics subpage), each with a
`redirects` entry for its old path. An orphan sweep in August 2026 probed the
terms that the old Teaching index listed without links (2020 Fall through 2023
Spring at A&M, the 2024–25 UCI terms, 2013 Spring, 2009 Fall) and found no
unlinked pages, so the migration is complete.
