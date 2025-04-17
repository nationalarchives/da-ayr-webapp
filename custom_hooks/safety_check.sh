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
    pip install safety==3.4.0b8
fi

# Export requirements and run pip-audit
poetry export --format requirements.txt > requirements-temp.txt && pip-audit --requirement requirements-temp.txt && rm requirements-temp.txt
