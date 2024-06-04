#!/bin/bash
set -e

# Install poetry if not installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Installing..."
    curl -sSL https://install.python-poetry.org | python -
fi

# Install safety if not installed
if ! command -v safety &> /dev/null; then
    echo "Safety is not installed. Installing..."
    pip install safety
fi

poetry export --without-hashes -f requirements.txt | safety check --full-report --stdin --ignore=70612
