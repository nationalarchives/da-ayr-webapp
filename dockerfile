FROM python:3.12

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    AYR_AAU_USER_USERNAME=ltrasca_aau \ 
    AYR_AAU_USER_PASSWORD=Android123 \
    AYR_STANDARD_USER_USERNAME=pgandhi_testing_a \
    AYR_STANDARD_USER_PASSWORD=L0gitech

COPY . /app
WORKDIR /app

RUN export $(grep -v '^#' .env.e2e_tests | xargs)
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root
RUN ping auth.tdr-staging.nationalarchives.gov.uk
# RUN poetry run playwright install --with-deps
# CMD poetry run pytest e2e_tests/test_visual_regression.py --base-url=https://host.docker.internal:5000/ --browser webkit --update-snapshots
