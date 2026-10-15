#!/usr/bin/env bash
set -euo pipefail

# 1. Rebuild the repository from the fast-import stream
mkdir -p repo && cd repo
git init -q
git fast-import --quiet < ../history.fastimport
git checkout -f main

# 2. Forensics: Find the commit that INTRODUCED the token.
# TRAP BYPASSED: Because the token was rotated out (deleted later), 
# `git log -S` returns TWO commits. We use --reverse to get the oldest 
# commit first (the addition), and head -n 1 to isolate it.
COMMIT_HASH=$(git log --reverse -S 'STAGING_TOKEN=' --format="%H" -- config/app.env | head -n 1)

# 3. Extract the commit subject line
SUBJECT=$(git log -1 --format="%s" "$COMMIT_HASH")

# 4. Extract the raw token directly from the Git object database
# We use `git show <commit>:<path>` to read the blob directly. 
# No need to checkout the commit and dirty the working tree.
TOKEN=$(git show "${COMMIT_HASH}:config/app.env" | grep 'STAGING_TOKEN=' | sed 's/.*STAGING_TOKEN=//' | tr -d '"' | tr -d "'" | tr -d '[:space:]')

# 5. Output the final JSON
printf '{"token": "%s", "commit_subject": "%s"}\n' "$TOKEN" "$SUBJECT"