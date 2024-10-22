# Variables
GOVUK_DIR="node_modules/govuk-frontend/dist/govuk"

# Remove existing GOV.UK Frontend assets
rm -rf app/static/fonts
rm -rf app/static/images
rm -rf app/static/govuk-frontend*

# Move govuk-frontend JS assets to static directory of app
cp $GOVUK_DIR/govuk-frontend.min.js* app/static/

# Tidy up
rm -rf app/static/assets
rm -rf app/static/VERSION.txt
