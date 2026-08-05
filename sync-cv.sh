#!/usr/bin/env bash
#
# sync-cv.sh — pull the latest CV out of the CV project and into this website.
#
#   ./sync-cv.sh
#
# What it does:
#   1. Runs generate_cv.py in the CV project against profiles/web-cv.yaml
#      (Markdown only) and against profiles/complete-cv.yaml (for the PDF).
#   2. Strips the generator's title block from the Markdown, since the website
#      supplies its own page heading, and writes generated/cv-body.md.
#   3. Copies the complete CV PDF to static/easwaran-cv.pdf.
#
# This is strictly one-way: nothing here writes into the CV project's data.
# Commit the results — the deployed site is built from what's in git, so
# GitHub never needs to see the CV project.

set -euo pipefail

# Where the CV project lives. Override by exporting CV_PROJECT before running.
CV_PROJECT="${CV_PROJECT:-$HOME/Library/CloudStorage/Dropbox/Claude/CV and AP-10}"

SITE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$CV_PROJECT" ]; then
  echo "error: CV project not found at:" >&2
  echo "  $CV_PROJECT" >&2
  echo "Set CV_PROJECT to the right path and try again." >&2
  exit 1
fi

echo "Generating from $CV_PROJECT ..."
cd "$CV_PROJECT"

python3 generate_cv.py profiles/web-cv.yaml --no-pdf
python3 generate_cv.py profiles/web-publications.yaml --no-pdf
python3 generate_cv.py profiles/complete-cv.yaml

mkdir -p "$SITE/generated" "$SITE/static"

# Keep everything from the first "## " heading onward. The generator emits a
# title block (name, contact line, "Updated ...") above that, which would
# duplicate the website's own page header.
awk '/^## /{found=1} found' build/web-cv.md          > "$SITE/generated/cv-body.md"
awk '/^## /{found=1} found' build/web-publications.md > "$SITE/generated/publications-list.md"

cp build/complete-cv.pdf "$SITE/static/easwaran-cv.pdf"

cd "$SITE"
for f in generated/cv-body.md generated/publications-list.md; do
  echo "  $f ($(wc -l < "$f" | tr -d ' ') lines)"
done
echo "  static/easwaran-cv.pdf"
echo "Now run:  python3 build.py --serve   to preview, then commit and push."
