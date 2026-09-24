#!/usr/bin/env bash
#
# Update CV.command — double-click in Finder to bring CV changes onto the website.
#
# Use it after editing anything in the CV project (../CV and AP-10/data/*.yaml):
# a new publication, a changed link, a new student. It
#
#   1. makes sure this folder is up to date with GitHub,
#   2. runs ./sync-cv.sh, which regenerates the CV page, the generated part of
#      the Publications page, and the CV PDF,
#   3. shows you exactly what changed,
#   4. and, if you say yes, commits those files (and only those) and pushes,
#      which makes GitHub rebuild the live site within a minute or so.
#
# Anything else you have uncommitted in this folder is left alone.

set -o pipefail
cd "$(dirname "$0")" || exit 1

# Finder-launched scripts don't always see Homebrew's tools (python3, typst).
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Never stop to ask for a GitHub username/password: GitHub doesn't accept
# account passwords here anyway, so a prompt is a dead end. Fail with advice.
export GIT_TERMINAL_PROMPT=0

SYNCED=(generated/cv-body.md generated/publications-list.md static/easwaran-cv.pdf)
bold=$'\e[1m'; red=$'\e[31m'; green=$'\e[32m'; yellow=$'\e[33m'; off=$'\e[0m'

finish() {
  echo
  read -r -p "Press Return to close this window. " _
  exit "${1:-0}"
}

echo "${bold}Updating the website from the CV project${off}"
echo

# A zero-byte lock left behind by an interrupted git command blocks every commit.
if [ -e .git/index.lock ]; then
  if pgrep -x git >/dev/null; then
    echo "${red}Another git command is running. Wait for it to finish and try again.${off}"
    finish 1
  fi
  echo "${yellow}Removing a stale .git/index.lock (no git command is running).${off}"
  rm -f .git/index.lock
fi

if [ "$(git branch --show-current)" != "main" ]; then
  echo "${red}This folder is on branch '$(git branch --show-current)', not main.${off}"
  echo "Switch back with:  git checkout main"
  finish 1
fi

# Anything already half-changed in the synced files would get swept into the
# commit, so stop rather than guess.
if ! git diff --quiet HEAD -- "${SYNCED[@]}"; then
  echo "${red}These files already have uncommitted changes:${off}"
  git status --short -- "${SYNCED[@]}"
  echo "Commit or discard them first, then run this again."
  finish 1
fi

echo "Checking GitHub for newer changes..."
if ! git pull --ff-only --quiet; then
  echo "${red}Couldn't update from GitHub (see above). Nothing was changed.${off}"
  finish 1
fi

echo
log=$(mktemp)
if ! ./sync-cv.sh 2>&1 | tee "$log"; then
  echo
  echo "${red}sync-cv.sh failed (see above). Nothing was committed.${off}"
  git checkout -- "${SYNCED[@]}" 2>/dev/null
  finish 1
fi

# If typst wasn't available the PDF wasn't rebuilt, and what got copied is an
# old build. Put the committed PDF back rather than publish a stale one.
pdf_note=""
if grep -qi "PDF skipped" "$log"; then
  git checkout -- static/easwaran-cv.pdf
  pdf_note="${yellow}Note: the PDF wasn't rebuilt (is typst installed?), so the CV PDF on the site is unchanged.${off}"
fi
rm -f "$log"

echo
if git diff --quiet -- "${SYNCED[@]}"; then
  echo "${green}Nothing changed — the website already matches the CV project.${off}"
  [ -n "$pdf_note" ] && echo "$pdf_note"
  finish 0
fi

echo "${bold}What changed:${off}"
echo
git --no-pager diff --stat -- "${SYNCED[@]}"
echo
git --no-pager diff --color=always --word-diff=color -- generated/
[ -n "$pdf_note" ] && { echo; echo "$pdf_note"; }

others=$(git status --porcelain | grep -v -F -e "generated/cv-body.md" -e "generated/publications-list.md" -e "static/easwaran-cv.pdf")
if [ -n "$others" ]; then
  echo
  echo "(Other uncommitted changes in this folder will be left alone:)"
  echo "$others"
fi

echo
read -r -p "${bold}Publish these changes to the live site? [y/N] ${off}" answer
if [[ ! "$answer" =~ ^[Yy] ]]; then
  echo "Not published. The updated files are still here; run this again or commit them yourself."
  finish 0
fi

git add -- "${SYNCED[@]}"
if ! git commit --quiet -m "Update CV from CV project" -- "${SYNCED[@]}"; then
  echo "${red}The commit failed (see above).${off}"
  finish 1
fi
if ! git push --quiet; then
  echo
  echo "${yellow}Committed here, but this Terminal isn't signed in to GitHub, so it couldn't push.${off}"
  echo "To publish now: open GitHub Desktop and click \"Push origin\"."
  echo "To let this script push by itself next time, sign in once from Terminal"
  echo "(see \"Signing in to GitHub from Terminal\" in README.md)."
  finish 1
fi

echo
echo "${green}Done. The site will be live in a minute or two:${off} https://www.kennyeaswaran.org/publications/"
echo "Build progress: https://github.com/kennyeaswaran/kennyeaswaran.github.io/actions"
finish 0
