#!/bin/bash
set +e

export $(grep -v '^#' .env.e2e_tests | xargs)
OUTPUT=$(npx pa11y-ci --config configs/pa11y_ci_precommit.js)
echo "${OUTPUT}"

set -e
