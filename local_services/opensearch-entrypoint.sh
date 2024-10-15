#!/bin/bash

# Wait until OpenSearch is available
until curl -s -k -u admin:"$OPENSEARCH_INITIAL_ADMIN_PASSWORD" https://localhost:9200 -o /dev/null; do
  echo "Waiting for OpenSearch to be available..."
  sleep 5
done

# Register the snapshot repository if it doesn't already exist
curl -s -k -X PUT "https://localhost:9200/_snapshot/my-fs-repository" \
  -u admin:"$OPENSEARCH_INITIAL_ADMIN_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "fs",
    "settings": {
      "location": "/mnt/snapshots"
    }
  }'

# Restore from snapshot
curl -s -k -X POST "https://localhost:9200/_snapshot/my-fs-repository/1/_restore" \
  -u admin:"$OPENSEARCH_INITIAL_ADMIN_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "indices": "documents",
    "include_global_state": false
  }'

echo "Restore completed."
exec "$@"
