FROM alpine:3.20

RUN apk add --no-cache openssl bash

WORKDIR /certs

# Create directories
RUN mkdir -p /certs/webapp_postgres_certs /certs/opensearch_certs

# Copy scripts
COPY ./webapp_postgres_certs/generate_webapp_postgres_certs.sh /certs/webapp_postgres_certs/
COPY ./opensearch_certs/generate_opensearch_certs.sh /certs/opensearch_certs/

# Make scripts executable
RUN chmod +x /certs/webapp_postgres_certs/generate_webapp_postgres_certs.sh \
    && chmod +x /certs/opensearch_certs/generate_opensearch_certs.sh

# Set the entrypoint to run the certificate generation
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/certs/webapp_postgres_certs/generate_webapp_postgres_certs.sh && /certs/opensearch_certs/generate_opensearch_certs.sh"]
