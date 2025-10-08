#!/bin/bash
set -e

# Directories
OPENSEARCH_CERTS_DIR=/opensearch_certs
WEBAPP_POSTGRES_CERTS_DIR=/webapp_postgres_certs
MINIO_CERTS_DIR=/minio_certs

# Create directories if they don't exist
mkdir -p $OPENSEARCH_CERTS_DIR $WEBAPP_POSTGRES_CERTS_DIR $MINIO_CERTS_DIR

# Generate Root CA
if [ ! -f $OPENSEARCH_CERTS_DIR/root-ca.pem ]; then
  openssl genrsa -out $OPENSEARCH_CERTS_DIR/root-ca.key 4096
  openssl req -x509 -new -nodes -key $OPENSEARCH_CERTS_DIR/root-ca.key -sha256 -days 3650 -out $OPENSEARCH_CERTS_DIR/root-ca.pem -subj "/C=GB/L=Test/O=Test/OU=SSL/CN=RootCA"
fi

# Function to generate certificates with SAN
generate_cert() {
  local name=$1
  local cert_dir=$2
  local cn=$3
  local san=$4
  # Create a temporary config file for SAN
  cat > $cert_dir/$name-san.cnf <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn
[dn]
C = GB
L = Test
O = Test
OU = SSL
CN = $cn
[req_ext]
subjectAltName = $san
EOF
  openssl genrsa -out $cert_dir/$name.key 2048
  openssl req -new -key $cert_dir/$name.key -out $cert_dir/$name.csr -config $cert_dir/$name-san.cnf
  openssl x509 -req -in $cert_dir/$name.csr -CA $OPENSEARCH_CERTS_DIR/root-ca.pem -CAkey $OPENSEARCH_CERTS_DIR/root-ca.key -CAcreateserial -out $cert_dir/$name.crt -days 365 -sha256 -extensions req_ext -extfile $cert_dir/$name-san.cnf
  rm $cert_dir/$name.csr $cert_dir/$name-san.cnf
}

# Generate certificates with SANs
generate_cert "opensearch-node1" $OPENSEARCH_CERTS_DIR "opensearch-node1" "DNS:opensearch-node1,IP:127.0.0.1"
generate_cert "opensearch-node2" $OPENSEARCH_CERTS_DIR "opensearch-node2" "DNS:opensearch-node2,IP:127.0.0.1"
generate_cert "postgres_localhost" $WEBAPP_POSTGRES_CERTS_DIR "localhost" "DNS:localhost,IP:127.0.0.1"
generate_cert "minio" $MINIO_CERTS_DIR "minio" "DNS:minio,IP:127.0.0.1"

# Copy root CA to other directories
cp $OPENSEARCH_CERTS_DIR/root-ca.pem $WEBAPP_POSTGRES_CERTS_DIR/
cp $OPENSEARCH_CERTS_DIR/root-ca.pem $MINIO_CERTS_DIR/root-ca.crt

# Set permissions
chmod 400 $OPENSEARCH_CERTS_DIR/* $WEBAPP_POSTGRES_CERTS_DIR/* $MINIO_CERTS_DIR/*
chown 999:999 $WEBAPP_POSTGRES_CERTS_DIR/*
