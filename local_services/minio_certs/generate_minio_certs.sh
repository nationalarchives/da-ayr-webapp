# Create a private key
openssl genrsa -out root-ca.key 2048

# Generate a root CA
openssl req -x509 -new -nodes -key root-ca.key -sha256 -out root-ca.crt -subj "/CN=RootCA"

openssl genrsa -out minio.key 2048

# Create a self-signed certificate
openssl req -new -key minio.key -out minio.csr -subj "/CN=localhost"

# Create a CA certificate
openssl x509 -req -in minio.csr -CA root-ca.crt -CAkey root-ca.key -CAcreateserial -out minio.crt -days 365 -sha256

chown 999:999 minio.key root-ca.key
