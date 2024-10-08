# Create a private key
openssl genrsa -out root-ca.key 2048

# Generate a root CA
openssl req -x509 -new -nodes -key root-ca.key -sha256 -out root-ca.pem -subj "/CN=RootCA"

# Generate a server key
openssl genrsa -out opensearch-node1.key 2048
openssl genrsa -out opensearch-node2.key 2048

# Generate a certificate signing request (CSR)
openssl req -new -key opensearch-node1.key -out opensearch-node1.csr -subj "/CN=opensearch-node1"
openssl req -new -key opensearch-node2.key -out opensearch-node2.csr -subj "/CN=opensearch-node2"

# Sign the CSR with the root CA
openssl x509 -req -in opensearch-node1.csr -CA root-ca.pem -CAkey root-ca.key -CAcreateserial -out opensearch-node1.crt -days 365 -sha256
openssl x509 -req -in opensearch-node2.csr -CA root-ca.pem -CAkey root-ca.key -CAcreateserial -out opensearch-node2.crt -days 365 -sha256
