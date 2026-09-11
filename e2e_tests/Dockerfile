
FROM mcr.microsoft.com/playwright/python:v1.62.0-noble@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d

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
