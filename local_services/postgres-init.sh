#!/bin/bash
set -e

echo "Running postgres-init.sh script..."
echo "PGDATA is: $PGDATA"

# Configure PostgreSQL to allow external connections
echo "host all all 0.0.0.0/0 scram-sha-256" >> "$PGDATA/pg_hba.conf"

echo "PostgreSQL configured for external connections"
echo "pg_hba.conf contents:"
cat "$PGDATA/pg_hba.conf" | tail -5
