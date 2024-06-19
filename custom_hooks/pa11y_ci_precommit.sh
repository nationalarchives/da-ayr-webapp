#!/bin/bash
set +e

if [ "$CI" = "true" ]; then exit 0; fi

python e2e_tests/utils_scripts/user_management.py -m create -o pa11y -rn $KEYCLOAK_REALM_NAME -cid $KEYCLOAK_CLIENT_ID -cs $KEYCLOAK_CLIENT_SECRET -uri $KEYCLOAK_BASE_URI -ut aau

OUTPUT=$(npx pa11y-ci --config configs/pa11y_config.json)
echo "${OUTPUT}"

USER_ID=`cat configs/user_id.txt`

echo $USER_ID

python e2e_tests/utils_scripts/user_management.py -m delete -rn $KEYCLOAK_REALM_NAME -cid $KEYCLOAK_CLIENT_ID -cs $KEYCLOAK_CLIENT_SECRET -uri $KEYCLOAK_BASE_URI -uid $USER_ID

rm configs/pa11y_config.json configs/user_id.txt
set -e
