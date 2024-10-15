# Create a private key
openssl genrsa -out root-ca.key 2048

# Generate a root CA
openssl req -x509 -new -nodes -key root-ca.key -sha256 -out root-ca.pem -subj "/CN=RootCA"

openssl genrsa -out postgres_localhost.key 2048

# Create a self-signed certificate
openssl req -new -key postgres_localhost.key -out postgres_localhost.csr -subj "/CN=localhost"

# (Optional) Create a CA certificate
openssl x509 -req -in postgres_localhost.csr -CA root-ca.pem -CAkey root-ca.key -CAcreateserial -out postgres_localhost.crt -days 365 -sha256
