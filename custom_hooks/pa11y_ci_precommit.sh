#!/bin/bash
set +e

export $(grep -v '^#' .env.e2e_tests | xargs)

# Install pa11y-ci if not installed
npm list | grep pa11y-ci || npm install --save-dev pa11y-ci --no-shrinkwrap
OUTPUT=$(npm run precommit)
echo "${OUTPUT}"

set -e
