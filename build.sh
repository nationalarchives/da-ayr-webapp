# Variables
GOVUK_DIR="node_modules/govuk-frontend/dist/govuk"

# Remove existing GOV.UK Frontend assets
rm -rf app/static/fonts
rm -rf app/static/images
rm -rf app/static/govuk-frontend*

# Install npm packages
npm i

# Move govuk-frontend JS assets to static directory of app
cp $GOVUK_DIR/govuk-frontend* app/static/
cp $GOVUK_DIR/all.scss app/static/_all.scss

# Tidy up
rm -rf app/static/assets
rm -rf app/static/VERSION.txt
