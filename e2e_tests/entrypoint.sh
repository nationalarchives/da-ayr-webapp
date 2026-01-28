#!/bin/bash
set -e

# Checkout the specified git ref if not main (in case build ARG didn't do it)
if [ "$GIT_REF" != "main" ]; then
  git fetch --all && git checkout "$GIT_REF"
fi


# If TEST_FILTER is empty or '.', run all tests
if [ -z "$TEST_FILTER" ] || [ "$TEST_FILTER" = "." ]; then
    TEST_PATH="."
else
    TEST_PATH="$TEST_FILTER"
fi

# Run tests for each browser specified in BROWSERS (comma-separated)
IFS=',' read -ra BROWSER_LIST <<< "$BROWSERS"
for BROWSER in "${BROWSER_LIST[@]}"; do
    echo "Running tests for browser: $BROWSER, test filter: $TEST_PATH"
    pytest -vvv -s "$TEST_PATH" \
        --base-url=https://127.0.0.1:5000 \
        --browser "$BROWSER" \
        --update-snapshots \
        --html=playwright-report/report.html \
        --self-contained-html
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo "Tests failed for browser: $BROWSER"
        exit $EXIT_CODE
    fi
done
