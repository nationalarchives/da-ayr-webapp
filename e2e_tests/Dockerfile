
FROM mcr.microsoft.com/playwright/python:v1.64.1-noble@sha256:330d401ae23c905896a0c26c66c36fc971b621519e7b11b435a8328d7bf6e031

HEALTHCHECK NONE

WORKDIR /e2e_tests

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Accept build-time and run-time arguments
ARG GIT_REF=main
ENV GIT_REF=${GIT_REF}
ARG BROWSERS="chromium"
ENV BROWSERS=${BROWSERS}
ARG TEST_FILTER="."
ENV TEST_FILTER=${TEST_FILTER}

# Checkout the specified git ref if not main
RUN if [ "$GIT_REF" != "main" ]; then git fetch --all && git checkout "$GIT_REF"; fi

# Entrypoint script to handle parameters
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER root

ENTRYPOINT ["/entrypoint.sh"]
