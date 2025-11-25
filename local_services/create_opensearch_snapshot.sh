#!/bin/bash

# Script to create an OpenSearch snapshot with all indexed data
# This snapshot can be used to restore data on other machines

set -e

OPENSEARCH_HOST="${OPENSEARCH_HOST:-http://localhost:9200}"
OPENSEARCH_PASSWORD="${OPENSEARCH_INITIAL_ADMIN_PASSWORD}"

# Build curl auth options if password is set
if [ -n "$OPENSEARCH_PASSWORD" ]; then
    AUTH_OPTS="-u admin:${OPENSEARCH_PASSWORD} -k"
    echo "Using authentication"
else
    AUTH_OPTS=""
    echo "No authentication (security disabled)"
fi

echo "Creating OpenSearch snapshot"

# Register the snapshot repository if it doesn't already exist
echo "Registering snapshot repository"
curl ${AUTH_OPTS} -X PUT "${OPENSEARCH_HOST}/_snapshot/my-fs-repository" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "fs",
    "settings": {
      "location": "/mnt/snapshots"
    }
  }'

echo -e "\n"

# Delete existing snapshot if it exists
echo "Deleting existing snapshot (if any)"
curl ${AUTH_OPTS} -X DELETE "${OPENSEARCH_HOST}/_snapshot/my-fs-repository/1" || true

echo -e "\n"

# Create new snapshot
echo "Creating new snapshot"
curl ${AUTH_OPTS} -X PUT "${OPENSEARCH_HOST}/_snapshot/my-fs-repository/1?wait_for_completion=true" \
  -H 'Content-Type: application/json' \
  -d '{
    "indices": "documents",
    "include_global_state": false
  }'

echo -e "\n"

# Verify snapshot
echo "Verifying snapshot"
curl ${AUTH_OPTS} -X GET "${OPENSEARCH_HOST}/_snapshot/my-fs-repository/1"

echo -e "\n\nSnapshot created successfully"
echo "The snapshot is stored in local_services/snapshots/"
