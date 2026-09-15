#!/bin/bash

set -ex

# Create a private key
openssl genrsa -out root-ca.key 2048

# Generate a root CA
openssl req -x509 -new -nodes -key root-ca.key -sha256 -out root-ca.crt -subj "/CN=RootCA"

# Generate certificate and key
openssl genrsa -out rustfs.key 2048

# Create a self-signed certificate
openssl req -new -key rustfs.key -out rustfs.csr -subj "/CN=localhost"

# Create a CA certificate
openssl x509 -req -in rustfs.csr -CA root-ca.crt -CAkey root-ca.key -CAcreateserial -out rustfs.crt -days 365 -sha256

# When running as root inside containers, align ownership with service user.
if [ "$(id -u)" -eq 0 ]; then
	chown 999:999 rustfs.key root-ca.key
fi
