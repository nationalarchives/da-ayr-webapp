#!/bin/bash
set -e

WEBAPP_PORT=${WEBAPP_PORT}

REALM_FILE="/opt/keycloak/data/import/realm-export.json"
TEMP_FILE="/tmp/realm-export-temp.json"

# Use sed to replace all instances of port 5003 with the configured port
# Replace both in URLs (:5003/) and in port strings (:5003")
sed -E 's/:[0-9]+/:'"$WEBAPP_PORT"'/g' \
    "$REALM_FILE" > "$TEMP_FILE"

mv "$TEMP_FILE" "$REALM_FILE"

exec /opt/keycloak/bin/kc.sh start-dev \
    --import-realm \
    --spi-login-protocol-openid-connect-legacy-logout-redirect-uri=true