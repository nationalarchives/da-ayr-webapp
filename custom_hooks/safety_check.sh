#!/bin/bash
set -e

# Install poetry if not installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Installing..."
    curl -sSL https://install.python-poetry.org | python -
fi

# Ensure poetry-plugin-export is available (required for Poetry 2.x)
if ! poetry self show plugins 2>/dev/null | grep -q "poetry-plugin-export"; then
    echo "Installing poetry-plugin-export..."
    poetry self add poetry-plugin-export
fi

# Install safety if not installed
if ! command -v safety &> /dev/null; then
    echo "Safety is not installed. Installing..."
    pip install safety==3.6.1
fi

# The --ignore flag was added here because the vulnerability with ID 70612 as reported by Safety CLI exists for all the latest versions of Jinja, it can be removed once fixed
poetry export --without-hashes -f requirements.txt | safety check --full-report --stdin --ignore=70612
