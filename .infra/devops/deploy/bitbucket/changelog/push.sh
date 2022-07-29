#!/usr/bin/env bash

set -e

# Usage "sh .infra/devops/deploy/bitbucket/changelog/push.sh"

API_VERSION=$(cat version)

# Path to Changelog Markdown template
CHANGELOG_TEMPLATE_PATH=".infra/devops/deploy/bitbucket/changelog/template.md"

# ChangeLog data content will be passed to nodejs using temp file
CHANGELOG_CONTENT_TEMP_PATH=".infra/devops/deploy/bitbucket/changelog/rendered.temp"

echo 
echo "Render changelog from Git log..."
git show $BITBUCKET_COMMIT --pretty=format:"Original Commit ID: %h%n%n## Changes%n%B" --no-patch > $CHANGELOG_CONTENT_TEMP_PATH

# Write rendered changelog
node .infra/devops/deploy/bitbucket/changelog/write.js $CHANGELOG_TEMPLATE_PATH $CHANGELOG_CONTENT_TEMP_PATH

echo
echo "Committing Changelog to current branch..."

# Add CHANGELOG.md file in tracked files to commit
git add CHANGELOG.md

# Commit tracked file with message [skip ci] so that pipeline won't be triggered
git commit -m "[skip ci] update changelog for v$PACKAGE_VERSION"

# Push committed change to the current repo.
git push origin
