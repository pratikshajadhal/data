#!/usr/bin/env bash

set -e

# Usage "sh .infra/devops/deploy/bitbucket/changelog/push.sh"

API_VERSION=$(cat version)

echo
echo "Committing Changelog to current branch..."

# Add CHANGELOG.md file in tracked files to commit
git add CHANGELOG.md

# Commit tracked file with message [skip ci] so that pipeline won't be triggered
git commit -m "[skip ci] update changelog for v$API_VERSION"

# Push committed change to the current repo.
git push origin
