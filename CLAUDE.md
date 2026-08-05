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

`profiles/web-cv.yaml` lives in the CV project and deliberately omits
publications and talks: the website has its own Publications page, and the full
talk list is better served by the PDF.

Generated output is committed so that GitHub Actions never needs access to the
CV project.

**Not yet wired up:** the Publications page is hand-maintained, because
`data/publications.yaml` stores one `url` per entry (the publisher/DOI link)
and has no field for the Dropbox preprint PDFs that the page links from every
title. Generating it from the store would silently drop those. Adding an
optional `pdf:` field to the store and backfilling it would let the Publications
page work the same way the CV page does.

## Provenance

Built August 2026, migrating content from the Google Sites version of
kennyeaswaran.org. Stale facts corrected during migration: the rank at UC
Irvine (Professor, not Associate Professor), leftover Texas A&M links on the
home page, and a Texas A&M link for Matthew Sheldon's UCI affiliation.
