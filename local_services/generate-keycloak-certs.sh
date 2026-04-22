#!/bin/bash
# Generates a self-signed TLS certificate for Keycloak's HTTPS listener.
# Required for webkit-based e2e tests: webkit enforces the Secure cookie flag
# strictly and will not store Secure cookies received over HTTP, causing the
# Keycloak auth session to be lost before form submission.
#
# Run once before starting docker compose:
#   ./local_services/generate-keycloak-certs.sh
set -e

CERT_DIR="$(dirname "$0")/keycloak_certs"
mkdir -p "$CERT_DIR"

openssl req -x509 -newkey rsa:2048 -nodes \
  -out "$CERT_DIR/cert.pem" \
  -keyout "$CERT_DIR/key.pem" \
  -days 3650 \
  -subj '/CN=keycloak' \
  -addext 'subjectAltName=DNS:keycloak,DNS:localhost,IP:127.0.0.1'

echo "Keycloak certs written to $CERT_DIR"
