#!/bin/bash
set -e

if [ "$CI" = "true" ]; then exit 0; fi

if [ ! -f ".env.e2e_tests" ]; then
	echo "Skipping pa11y-ci: .env.e2e_tests not found."
	exit 0
fi

set -a
source .env.e2e_tests
set +a

npx pa11y-ci --config configs/pa11y_ci_precommit.js
