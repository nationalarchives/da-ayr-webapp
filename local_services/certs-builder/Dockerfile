FROM alpine:3.20

RUN apk add --no-cache openssl bash

WORKDIR /certs

COPY ./webapp_postgres_certs ./webapp_postgres_certs
COPY ./opensearch_certs ./opensearch_certs

RUN chmod +x ./webapp_postgres_certs/generate_webapp_postgres_certs.sh \
    && chmod +x ./opensearch_certs/generate_opensearch_certs.sh \
    && ./webapp_postgres_certs/generate_webapp_postgres_certs.sh \
    && ./opensearch_certs/generate_opensearch_certs.sh
