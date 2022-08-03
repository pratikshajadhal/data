#!/usr/bin/env bash

set -e

# Usage "sh .infra/devops/deploy/bitbucket/changelog/write.sh"

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
