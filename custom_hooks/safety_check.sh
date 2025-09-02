#!/bin/bash
set -e

# Install poetry if not installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Installing..."
    curl -sSL https://install.python-poetry.org | python -
fi

# Ensure correct safety and typer versions
echo "Ensuring compatible safety and typer versions..."
pip install --force-reinstall typer==0.9.0
pip install --force-reinstall --no-deps safety==2.3.5
# The --ignore flag was added here because the vulnerability with ID 70612 as reported by Safety CLI exists for all the latest versions of Jinja, it can be removed once fixed
poetry export --without-hashes -f requirements.txt
safety check --full-report --stdin --ignore=70612
