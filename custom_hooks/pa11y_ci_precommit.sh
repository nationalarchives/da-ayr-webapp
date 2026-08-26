#!/bin/bash
set -euo pipefail

if [[ "${CI:-}" == "true" ]]; then
	exit 0
fi

ENV_FILE="${PA11Y_ENV_FILE:-.env.e2e_tests}"

if [[ ! -f "${ENV_FILE}" ]]; then
	echo "Pa11y skipped: ${ENV_FILE} not found"
	exit 0
fi

set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

npx pa11y-ci --config configs/pa11y_ci_precommit.js
