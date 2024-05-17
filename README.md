# DA AYR Beta WebApp

This is a repo created and maintained by The National Archives for the Access Your Records (AYR) project. It holds a Flask application based from the [Land Registry GOV.UK Frontend Flask template repo](https://github.com/LandRegistry/govuk-frontend-flask). Currently the intention is to deploy this via AWS Lambda and API Gateway but you can run it however you would like.

## Getting started

### Setup Poetry environment

[Install poetry](https://python-poetry.org/docs/)
Check poetry has been installed using:

```shell
poetry --version
```

Then install the required dependencies using:

```shell
poetry install
```

You can now access the virtual environment created by poetry with:

```shell
poetry shell
```

in which you can run all of the following commands. Alternatively you can prefix all of the following commands with `poetry run`.

### Install PostgreSQL

PostgrSQL is a dependency required for running unit tests, which are reliant on [testing.postgresql](https://github.com/tk0miya/testing.postgresql).
[Download & Install PostgreSQL](https://www.postgresql.org/download/)

To verify that PostgreSQL is installed on your machine you can use:

```shell
psql --version
```

and

```shell
initdb --version
```

Optionally, you can also install pgAdmin for easier administration and monitoring of the PostgreSQL database. PgAdmin is a tool that provides a modern GUI and tools that make it easier to perform actions.

[(Optional) Download & Install pgAdmin](https://www.pgadmin.org/download/)

### Set up commit signing

GitHub rulesets for the AYR repo prevent pull requests that contain unsigned commits from being merged with the main branch. To avoid having to modify PRs that contain unsigned commits, you should configure signed commits before making a first PR using the guide below.

[Configure signed commits using the TDR dev documentation](https://github.com/nationalarchives/tdr-dev-documentation/blob/master/manual/development-setup/signed-commits.md)

### Get GOV.UK Frontend assets

For convenience a shell script has been provided to download and extract the GOV.UK Frontend distribution assets

```shell
./build.sh
```

### CSS / SCSS

We have the `app/static/src/scss/main.scss` file in the repo which we include all scss via partial scss files.

This needs to be converted using `sass` to a `app/static/src/css/main.css` file which we include in the `app/templates/base.html` template which we use as a base for all of our html files.

To build `main.css` file you can run the npm build script which runs `sass` by first installing the npm packages and then using:

```shell
npm run build
```

or if you'd like to watch for changes use:

```shell
npm run dev
```

To lint all CSS use:

```shell
npm run lint
```

### SCSS files

If you need to add any new style files, then you can create a [partial scss](https://sass-lang.com/guide/#partials) file, with filename prefixed by an underscore to mark it as such and then include it in the main.scss file using `@import`.

e.g. for `_foo.scss`, add `@import "includes/foo";`.

### Set up SSL Certificate

For local development we have decided to require an SSL certificate so that we run our development server with SSL so we are closer to a production system where we intend to use SSL also. We specify the flask cli flags `FLASK_RUN_CERT=cert.pem` and `FLASK_RUN_KEY=key.pem` in the `.flaskenv`, which expect a `cert.pem` and corresponding `key.pem` file in the root of the repo.

You will need to create the cert-key pair with:

  ```shell
  poetry run openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
  ```

  and fill out the its prompts with information that you want (it does not matter as it is only being used for a development server).

  **Note:** this command creates a cert-key pair valid for 365 days, but you can amend this as you wish.

When you access the application in a new browser for the first time with one of these keys you will have to tell it you trust the certificate, but then you should not be asked again.

**Note:** [flask-talisman](###HTTP-security-headers) should redirect http requests to https but whenever running the flask development server with a certificate, this doesn't seem to do the redirection. We plan to investigate but for now we will have to deal without this redirection in local dev.

### Set Flask Configuration Variables

Set the Flask Configuration Variables either with either:

- Environment Variables:
  1. Set all desired environment variables for all of the variables specified in `.env.env_var.template`. For convenience you can do this by running the following in the root of the repo:

    ```shell
    cp .env.env_var.template .env
    ```

    and filling out the `.env` file as desired.

- AWS Secrets Manager values:
  1. Set up your AWS credentials or log into an AWS account with the AWS CLI environment so that the desired AWS IAM user or role is set up.
  2. Make sure all of the properties (not the hardcoded values) in the `BaseConfig` class are set in the AWS Secrets Manager for this account.
  3. Set all desired environment variables for all of the variables specified in `env.aws_secrets_manager.template`. For convenience you can do this by running the following in the root of the repo:

    ```shell
    cp .env.aws_secrets_manager.template .env
    ```

    and filling out the `.env` file as desired.

**Note:** `AWSSecretsManagerConfig` depends on a `boto3` session which, when developing locally, can be set to use a specific AWS Profile by setting the environment variable `DEFAULT_AWS_PROFILE`.

### Run app

Ensure you set the above environment variables in the `.env` file as appropriate before running the Flask application with:

```shell
flask run
```

You should now have the app running on <https://localhost:5000/>

**Note:** Unless you have changed the `FLASK_APP` value in the `.flaskenv` file to point to another application entrypoint other than `main_app`, you must specify the `CONFIG_SOURCE` environment variable (as populated by the env file templates), to be either `AWS_SECRETS_MANAGER` or `ENVIRONMENT_VARIABLES` otherwise `flask run` will raise an error.

## Flask App Configuration Details

Our application uses configuration values defined using [Flask Config classes](https://flask.palletsprojects.com/en/2.3.x/config/#development-production) to set up the application's settings and connect it to various services. The pattern we are using consists of a base config class, `BaseConfig`, which is where we specify any hardcoded values, and all other configurable values are defined as a property, for example:

```python
    @property
    def EXAMPLE_VARIABLE(self):
        return self._get_config_value("EXAMPLE_VARIABLE")
```

where `_get_config_value` is treated as an abstract method which is implemented in the child config classes that extend `BaseConfig`.

Hardcoded values:

- `SESSION_COOKIE_HTTPONLY`: Configure session cookies to be HTTP-only. Is `True`.
- `SESSION_COOKIE_SECURE`: Configure session cookies to be secure. Is `True`.
- `CONTACT_EMAIL`: Email address for contact information.
- `CONTACT_PHONE`: Phone number for contact information.
- `DEPARTMENT_NAME`: The name of the department.
- `DEPARTMENT_URL`: The URL of the department's website.
- `SERVICE_NAME`: The name of the service.
- `SERVICE_PHASE`: The phase of the service.
- `SERVICE_URL`: The URL of the service.

Properties configurable at runtime:

- `AWS_REGION`: The AWS region used for AWS services.
- `DB_PORT`: The port of the database to connect to.
- `DB_HOST`: The host of the database to connect to.
- `DB_USER`: The username of the database to connect to.
- `DB_PASSWORD`: The password of the database to connect to.
- `DB_NAME`: The name of the database to connect to.
- `KEYCLOAK_BASE_URI`: The base URI of the Keycloak authentication service.
- `KEYCLOAK_CLIENT_ID`: The client ID used for Keycloak authentication.
- `KEYCLOAK_REALM_NAME`: The name of the Keycloak realm.
- `KEYCLOAK_CLIENT_SECRET`: The client secret used for Keycloak authentication.
- `SECRET_KEY`: Secret key used for Flask session and security.
- `DEFAULT_PAGE_SIZE`: set value for no. of records to show on browse/search view.
- `DEFAULT_DATE_FORMAT`: set value to show date in specific format cross the application. i.e. "DD/MM/YYYY"
- `RECORD_BUCKET_NAME`: name of s3 bucket that holds all of the record objects themselves
- `FLASKS3_ACTIVE`: whether to fetch static assets from s3/Cloudfront rather than the usual `url_for`.
- `FLASKS3_CDN_DOMAIN`: CDN domain to fetch assets from if `FLASKS3_ACTIVE` is set to `True`
- `FLASKS3_BUCKET_NAME`: S3 bucket assets are uploaded to and served to Cloudfront from.

Calculated values:

- `SQLALCHEMY_DATABASE_URI`: The PostgreSQL database URI with format `postgresql+psycopg2://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>`.

We have two usable configs which extend `BaseConfig` for running the application:

- `EnvConfig` which implements `_get_config_value` so it reads from environment variables.
- `AWSSecretsManagerConfig` which implements `_get_config_value` so it reads from AWS Secrets Manager values.

When configuring `flask run` run the app created by `main_app.py`, as we do with the line `export FLASK_APP=main_app` in the `.flaskenv`, we can either use `EnvConfig` or `AWSSecretsManagerConfig` by setting `CONFIG_SOURCE` as either `ENVIRONMENT_VARIABLES` or `AWS_SECRETS_MANAGER` respectively. If using `AWSSecretsManagerConfig`, then you must also set `AWS_SM_CONFIG_SECRET_ID` which is the secret id of the Secrets Manager secret used to read in all the config values.

We also have a `TestingConfig` that extends `BaseConfig` which is only used for Flask tests as detailed below. Its implementation of  `_get_config_value` returns an empty string for all the configurable properties just so we don't need to worry about setting values in tests we don't care about them in. We may revisit this, as the fact that config vars are unnecessary in some tests that access them seems like a code smell that could be worth addressing; specifying them in any test that needs them and refactoring the code if we still find asserting anything about them unnecessary could be a better approach long term.
As well as the confgiurable values discussed above, we also hardcode the following on the `TestingConfig`:

- `TESTING` to `True` to disable error catching (further info [here](https://flask.palletsprojects.com/en/3.0.x/config/#TESTING)), and changes certain extension's logic as well as own on (e.g. disables forcing of https) to facilitate easier testing.
- `SECRET_KEY` to `"TEST_SECRET_KEY"` so that Flask sessions work in the tests.

### The .flaskenv file

In addition to the `.env` file discussed above, which can be created from template files, we have a `.flaskenv` file with Flask specific configuration values which is committed to the repo and we don't expect to change these.

### Environment loading

Both the `.env` and `.flask_env` are loaded automatically when we run the flask application as outlined in the following section, thanks to the use of `python-dotenv`. More information on Flask environment variable hierarchies can be found [here](https://flask.palletsprojects.com/en/2.3.x/cli/#environment-variables-from-dotenv).

## Metadata Store Postgres Database

The webapp is set up to read data from an externally defined postgres database referred to as the Metadata Store.

We currently use the python package, Flask-SQLAlchemy to leverage some benefits of the ORM (Object Relationship Mapping) it provides, making our queries using the python classes we create as opposed to explicit SQL queries.

The database connection is configured with the `SQLALCHEMY_DATABASE_URI` variable built up in the Flask Config.

### Database Infrastructure and Connection

The database is assumed to be a PostgreSQL database.

This could be spun up by PostgreSQL or from Amazon RDS, for example.

When choosing the configuration choice `AWS_SECRETS_MANAGER`, we assume the database is an RDS database with an RDS proxy sitting in front, in the same AWS account as the Secrets Manager and lambda and resides in a VPC which the lambda is in so that the webapp hosted in the lambda can communicate with it securely.

### Database Tables, Schema and Data

We do not define the database tables ourselves, nor write any information to the database, both of which are assumed to be handled externally. To leverage the use of the ORM we reflect the tables from the existing database with the following line in our Flask app setup.

`db.Model.metadata.reflect(bind=db.engine, schema="public")`

More info on relecting database tables can be found [here](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/models/#reflecting-tables).

Further, to this, we do define models and columns from the corresponding tables we do use in our queries we use so that when developing we will know what attributes are available but this has to be manually kept in sync with the externally determined schema through discussion with the maintainers of the Metadata Store database.

### Dev database dump

Provided is the file `dev-data.sql` which can be used to restore a database on a postgres instance.
This is the database that is assumed to be used for our end to end tests which depend on data.
To use this database, you will need to:

1. connect to a database on a postgres instance with the user you want to own the new database: `psql -U username`
2. create a new database, e.g. `CREATE DATABASE ayr;`
3. exit from the `psql` connection
4. restore the data dump `dev-data.sql` with `psql -U username -d ayr -f dev-data.sql`

NOTE: The db info used here will need to be used in the config as detailed in the config section.

## Keycloak Local Setup

It is possible to set up a local Keylcoak instance for development of Keycloak authentication pages. This repository: https://github.com/nationalarchives/tdr-auth-server/blob/master/README.md contains a readme which can be used to setup Keycloak or follow the steps below.

1. Clone the TDR Auth Server repository
2. Sign in to Keycloak
3. Select realm settings
4. [Top right] Select Action dropdown
5. Select Partial Export
6. Save the file as ```tdr-realm-export.json``` in the root directory
7. Build the keycloak docker image using the following command
```
docker build -t tdr-auth-server .
```
8. Run the docker image with the following command:
```
docker run -it --rm --name tdr-auth-server -p 8081:8080 \
-e KEYCLOAK_ADMIN=admin \
-e KEYCLOAK_ADMIN_PASSWORD=admin \
-e KEYCLOAK_IMPORT=/keycloak-configuration/tdr-realm.json \
-e REALM_ADMIN_CLIENT_SECRET=someValue \
-e CLIENT_SECRET=someValue \
-e BACKEND_CHECKS_CLIENT_SECRET=someValue \
-e REPORTING_CLIENT_SECRET=someValue \
-e USER_ADMIN_CLIENT_SECRET=someValue \
-e ROTATE_CLIENT_SECRETS_CLIENT_SECRET=someValue \
-e KEYCLOAK_CONFIGURATION_PROPERTIES=intg_properties.json \
-e FRONTEND_URL=someValue \
-e GOVUK_NOTIFY_API_KEY_PATH=someValue \
-e GOVUK_NOTIFY_TEMPLATE_ID_PATH=someTemplateId \
-e DB_VENDOR=h2 \
-e SNS_TOPIC_ARN=someTopicArn \
-e TDR_ENV=intg \
-e KEYCLOAK_HOST=localhost:8081 \
-e KC_DB_PASSWORD=password \
-e BLOCK_SHARED_PAGES=false tdr-auth-server
```

9. Set the TDR Keycloak theme via the admin panel

Tip: the quickest way to view the TDR login theme (that is displayed to TDR users) is to (while logged into the console):

10. Select the "Master" Realm (top left, below the keycloak logo) if it's not already selected
11. Select "Realm roles" in the sidebar
12. Select "default-roles-master"
13. Select the "Themes" tab
14. Under "login theme", select "tdr" from the dropdown menu
15. Sign out (click "Admin" on the top right and select "Sign out")

Please see: https://github.com/nationalarchives/tdr-auth-server/blob/master/README.md#running-locally

### Update TDR Theme Locally

1. Rebuild the image locally and run. `docker build -t tdr-auth-server .`
2. Make necessary changes to the TDR theme (freemarker templates/sass/static resources)
3. Run following command from the root directory: `[root directory] $ npm run build-local --container_name=tdr-auth-server`
4. Refresh the locally running Keycloak pages to see the changes.
5. Repeat steps 3 to 5 as necessary.


## Testing

### Unit and Integration tests

For running flask app tests, we have the `client` fixture which uses the `app` fixture which utilises `TestingConfig` as discussed above.

To run the unit and integration tests you can run:

```shell
python -m pytest --cov=app --cov-report=term-missing --cov-branch -vvv
```

This also will generate a test coverage report.

#### Mocking user permissions in tests

We have 2 fixtures used for mocking a user and their permissions in our non end to end, flask tests:

- `mock_standard_user`
- `mock_all_access_user`

which can be called like

`mock_standard_user(client, "foo")`

`mock_all_access_user(client)`

respectively.

These mock the `get_user_groups` permissions helper which abstracts away the external api call to keycloak, which we do not want to call in our non end to end tests.

- `mock_standard_user` gives the user and results in an AYRUser where:
  - `can_access_ayr`: True
  - `is_standard_user`: True
  - `is_all_access_user`: False
  - `transferring_bodies`: same list as pass in as second arg to mock_standard_user

- `mock_standard_user` gives the user and results in an AYRUser where:
  - `can_access_ayr`: True
  - `is_standard_user`: False
  - `is_all_access_user`: True
  - `transferring_bodies`: None

### End-To-End Tests

We have a separate End To End suite of [Playwright](https://playwright.dev/python/docs/intro) tests in the `e2e_tests/` directory. These are also written in python and use the `pytest-playwright` `PyPi` package to run the tests as specified in the poetry dependencies.

In addition to installing the package, before you run the tests for the first time on your machine, you will need to run `playwright install` to install the required browsers for the end-to-end tests.

Before running our Playwright tests,

- `AYR_AAU_USER_USERNAME`
- `AYR_AAU_USER_PASSWORD`
- `AYR_STANDARD_USER_USERNAME`
- `AYR_STANDARD_USER_PASSWORD`

set environment variables with appropriate test user credentials for the instance you want to test

Note: a `.env.e2e_tests.template` file has been provided, which you can then `cp .env.e2e_tests.template .env.e2e_tests`, then fill, and then source `source .env.e2e_tests`

You can then run all of our Playwright tests against an instance, localhost for example, by running:

```shell
pytest e2e_tests/ --base-url=https://localhost:5000
```

You can swap out the base-url for another if you want to run the tests against another instance of the application.

To enable this flexibility we suggest any Playwright tests added to the repo use relative paths when referring to urls of the application itself.

In addition, we recommend that any tests that have dependencies on data, do not make assumptions about any particular database or instance involved, and instead do the test data set up and teardown as part of the test suite.

### Visual regression e2e tests

In order to ensure a consistent and stable testing environment, we make use of a [Docker](https://www.docker.com/products/docker-desktop/) image (and subsequently container) that is defined in structure inside of `e2e_tests/dockerfile`. Please note that the process of building and running the Docker container requires the same environment variables as the regular E2E tests talked about above. The `e2e_tests` directory contains a couple scripts that make the process of building and running the container simple:

First, switch current working directory to `e2e_tests`

```shell
cd e2e_tests/
```

Then, to build and run the E2E visual regression suite 

```shell
bash e2e_tests.reg_build_and_run.sh
```

To just run the E2E tests once the container has already been built

```shell
bash e2e_tests.reg_run.sh
```

Whilst the Docker container is running, snapshots of visual regression for pages that have been modified will be automatically saved inside of `e2e_tests/snapshots/test_css_no_visual_regression` and `e2e_tests/snapshots/test_css_no_visual_regression_mobile`.

### Useful playwright pytest run modes

#### browser

- To run the tests on specific browsers, as long as they have been installed already with `playwright install` you can add as many `--browser` flags as you want, e.g.

`pytest e2e_tests/ --base-url=https://localhost:5000 --browser chromium --browser firefox --browser webkit`

will run all the tests against `chromium`, `firefox` and `webkit`

#### headed

- To view the browser when the tests are running, you can add the `--headed` flag, e.g.

`pytest e2e_tests/ --base-url=https://localhost:5000 --headed`

#### PWDEBUG

- To utilise the playwright debugger, you can set the `PWDEBUG=1` environment variable, e.g.

`PWDEBUG=1 poetry run pytest e2e_tests/test_search.py --base-url=https://localhost:5000 --headed`

1. individual tests in file with multiple tests (use -k):
poetry run pytest e2e_tests/test_record_metadata.py -k test_page_title_and_header --base-url=https://localhost:5000 --headed

### Generate playwright tests using GUI

Run `poetry run playwright codegen https://localhost:5000 --ignore-https-errors` to spin up a browser instance which you can interact with, where each interaction will be captured as a pytest playwright line, which builds out a test skeleton file for you to add assertions to.

### When to add an E2E Tests?

End to end tests have prod and cons, such as the following:

Pros:

- Testing Real User Flows
- Complex User Scenarios (such as sign in flows)

Cons:

- Execution Time
- Harder to debug errors

Therefore we should try to add them sparingly on critical workflows.

### E2E Tests (Progressive Enhancement Support)

E2E Tests by default run without JavaScript & CSS.

To enable JavaScript to run during E2E Tests the flag `java_script_enabled` should be set to True within conftest.py.

To enable a test to run with CSS ensure each test is prefixed with with the term `test_css_test_name`.

e.g.:

`
def test_css_has_title(page: Page):
`

## Logging

### Configuration

The application logger configuration is detailed in `setup_logging` in `app/logger_config.py`.

This config includes:

- a formatter specifying request-specific information such as the remote address and URL when a request context is available
- setting the logging level to `INFO`.

`setup_logging` is called during the initialization of the Flask app.

### Usage

We can utilise the Flask logger by accessing Flask's `app.logger`. Since we define our routes with blueprints rather than the app directly, we can call access app through

```python
from flask import current_app
```

for example:

```python
current_app.logger.info('Some info message')
current_app.logger.debug('Some debug message')
current_app.logger.warning('Some warning message')
current_app.logger.error('Some error message')
```

### Output

The logs from the webapp, when used as above are output as a stream to stdout in the following format:

```sh
[2023-12-15 15:40:14,119] 127.0.0.1 requested https://localhost:5000/logger_test?log_level=error
ERROR in routes: Some error
```

### Extensions and package logs

Some of the Flask extensions used,as detailed in the Features section below, may produce their own logs and may have their own configuration and format different to the above.

### Testing logs

With pytest we can assert the logs we expect to be written by utilising pytest's inbuilt `caplog` fixture.

## Features

Please refer to the specific packages documentation for more details. Details can be found in the [pytest logging documentation](https://docs.pytest.org/en/7.1.x/how-to/logging.html#how-to-manage-logging).

### Forms generation and validation

Uses [Flask WTF](https://flask-wtf.readthedocs.io/en/stable/) and [WTForms](https://wtforms.readthedocs.io) to define and validate forms. Forms are rendered in your template using regular Jinja syntax.

### Form error handling

If a submitted form has any validation errors, an [error summary component](https://design-system.service.gov.uk/components/error-summary/) is shown at the top of the page, along with individual field [error messages](https://design-system.service.gov.uk/components/error-message/). This follows the GOV.UK Design System [validation pattern](https://design-system.service.gov.uk/patterns/validation/) and is built into the base page template.

### Flash messages

Messages created with Flask's `flash` function will be rendered using the GOV.UK Design System [notification banner component](https://design-system.service.gov.uk/components/notification-banner/). By default the blue "important" banner style will be used, unless a category of "success" is passed to use the green version.

### HTTP security headers

Uses [Flask Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) to set HTTP headers that can help protect against a few common web application security issues.

- Forces all connections to `https`, unless running with debug enabled or in testing. Note: This seems to not be working when running the local development with a SSL certificate as discussed [above](###set-up-ssl-certificate)
- Enables [HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security).
- Sets Flask's session cookie to `secure`, so it will never be set if your application is somehow accessed via a non-secure connection.
- Sets Flask's session cookie to `httponly`, preventing JavaScript from being able to access its content.
- Sets [X-Frame-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options) to `SAMEORIGIN` to avoid [clickjacking](https://en.wikipedia.org/wiki/Clickjacking).
- Sets [X-XSS-Protection](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection) to enable a cross site scripting filter for IE and Safari (note Chrome has removed this and Firefox never supported it).
- Sets [X-Content-Type-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options) to prevent content type sniffing.
- Sets a strict [Referrer-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy) of `strict-origin-when-cross-origin` that governs which referrer information should be included with requests made.

### Content Security Policy

A strict default [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) (CSP) is set using [Flask Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) to mitigate [Cross Site Scripting](https://developer.mozilla.org/en-US/docs/Web/Security/Types_of_attacks#cross-site_scripting_xss) (XSS) and packet sniffing attacks. This prevents loading any resources that are not in the same domain as the application.

### Response compression

Uses [Flask Compress](https://github.com/colour-science/flask-compress) to compress response data. This inspects the `Accept-Encoding` request header, compresses using either gzip, deflate or brotli algorithms and sets the `Content-Encoding` response header. HTML, CSS, XML, JSON and JavaScript MIME types will all be compressed.

## Support

This software is provided _"as-is"_ without warranty. Support is provided on a _"best endeavours"_ basis by the maintainers and open source community.

Please see the [contribution guidelines](CONTRIBUTING.md) for how to raise a bug report or feature request.
