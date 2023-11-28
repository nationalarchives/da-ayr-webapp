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

### Get GOV.UK Frontend assets

For convenience a shell script has been provided to download and extract the GOV.UK Frontend distribution assets

```shell
./build.sh
```

### CSS / SCSS

SASS is being used to build the local CSS files. To build the css files you can use npm to build by first installing the npm packages and then using:

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

- AWS SSM Parameter Store values:
  1. Set up your AWS credentials or log into an AWS account with the AWS CLI environment so that the desired AWS IAM user or role is set up.
  1. Make sure all of the properties (not the hardcoded values) in the `BaseConfig` class are set in the AWS SSM Parameter Store for this account.
  1. Set all desired environment variables for all of the variables specified in `env.aws_parameter_store.template`. For convenience you can do this by running the following in the root of the repo:

    ```shell
    cp .env.aws_parameter_store.template .env
    ```

    and filling out the `.env` file as desired.

**Note:** `AWSParameterStoreConfig` depends on a `boto3` session which, when developing locally, can be set to use a specific AWS Profile by setting the environment variable `DEFAULT_AWS_PROFILE`.

### Run app

Ensure you set the above environment variables in the `.env` file as appropriate before running the Flask application with:

```shell
flask run
```

You should now have the app running on <https://localhost:5000/>

**Note:** Unless you have changed the `FLASK_APP` value in the `.flaskenv` file to point to another application entrypoint other than `main_app`, you must specify the `CONFIG_SOURCE` environment variable (as populated by the env file templates), to be either `AWS_PARAMETER_STORE` or `ENVIRONMENT_VARIABLES` otherwise `flask run` will raise an error.

## Flask App Configuration Details

Our application uses configuration values defined using [Flask Config classes](https://flask.palletsprojects.com/en/2.3.x/config/#development-production) to set up the application's settings and connect it to various services. The pattern we are using consists of a base config class, `BaseConfig`, which is where we specify any hardcoded values, and all other configurable values are defined as a property, for example:

```python
    @property
    def EXAMPLE_VARIABLE(self):
        return self._get_config_value("EXAMPLE_VARIABLE")
```

where `_get_config_value` is treated as an abstract method which is implemented in the child config classes that extend `BaseConfig`.

Hardcoded values:

- `RATELIMIT_HEADERS_ENABLED`: Rate-limiting headers configuration. Is `True`.
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
- `SQLALCHEMY_DATABASE_URI`: The PostgreSQL database URI includes (username, password, hostname, dbname and dbport).
- `KEYCLOAK_BASE_URI`: The base URI of the Keycloak authentication service.
- `KEYCLOAK_CLIENT_ID`: The client ID used for Keycloak authentication.
- `KEYCLOAK_REALM_NAME`: The name of the Keycloak realm.
- `KEYCLOAK_CLIENT_SECRET`: The client secret used for Keycloak authentication.
- `KEYCLOAK_AYR_USER_GROUP`: The Keycloak user group used to check user access.
- `RATELIMIT_STORAGE_URI`: The URI for the Redis storage used for rate limiting.
- `SECRET_KEY`: Secret key used for Flask session and security.

We have two usable configs which extend `BaseConfig` for running the application:

- `EnvConfig` which implements `_get_config_value` so it reads from environment variables.
- `AWSParameterStoreConfig` which implements `_get_config_value` so it reads from AWS SSM Parameter Store values.

When configuring `flask run` run the app created by `main_app.py`, as we do with the line `export FLASK_APP=main_app` in the `.flaskenv`, we can either use `EnvConfig` or `AWSParameterStoreConfig` by setting `CONFIG_SOURCE` as either `ENVIRONMENT_VARIABLES` or `AWS_PARAMETER_STORE` respectively.

We also have a `TestingConfig` that extends `BaseConfig` which is only used for Flask tests as detailed below. Its implementation of  `_get_config_value` returns an empty string for all the configurable properties just so we don't need to worry about setting values in tests we don't care about them in. We may revisit this, as the fact that config vars are unnecessary in some tests that access them seems like a code smell that could be worth addressing; specifying them in any test that needs them and refactoring the code if we still find asserting anything about them unnecessary could be a better approach long term.
As well as the confgiurable values discussed above, we also hardcode the following on the `TestingConfig`:

- `TESTING` to `True` to disable error catching (further info [here](https://flask.palletsprojects.com/en/3.0.x/config/#TESTING)), and changes certain extension's logic as well as own on (e.g. disables forcing of https) to facilitate easier testing.
- `SECRET_KEY` to `"TEST_SECRET_KEY"` so that Flask sessions work in the tests.
- `WTF_CSRF_ENABLED` to `False` so that we do not need to worry about CSRF protection in our tests.

### The .flaskenv file

In addition to the `.env` file discussed above, which can be created from template files, we have a `.flaskenv` file with Flask specific configuration values which is committed to the repo and we don't expect to change these.

### Environment loading

Both the `.env` and `.flask_env` are loaded automatically when we run the flask application as outlined in the following section, thanks to the use of `python-dotenv`. More information on Flask environment variable hierarchies can be found [here](https://flask.palletsprojects.com/en/2.3.x/cli/#environment-variables-from-dotenv).

## Testing

### Unit and Integration tests

For running flask app tests, we have the `client` fixture which uses the `app` fixture which utilises `TestingConfig` as discussed above.

To run the unit and integration tests you can run:

```shell
python -m pytest --cov=app --cov-report=term-missing --cov-branch -vvv
```

This also will generate a test coverage report.

### End To End Tests

We have a separate End To End suite of [Playwright](https://playwright.dev/python/docs/intro) tests in the `e2e_tests/` directory. These are also written in python and use the `pytest-playwright` `PyPi` package to run the tests as specified in the poetry dependencies.

In addition to installing the package, before you run the tests for the first time on your machine, you will need to run `playwright install` to install the required browsers for the end to end tests.

You can then run all of our Playwright tests against localhost with:

```shell
pytest e2e_tests/ --base-url=https://localhost:5000
```

You can swap out the base-url for another if you want to run the tests against another instance of the application.

To enable this flexibility we suggest any Playwright tests added to the repo use relative paths when referring to urls of the application itself.

In addition, we recommend that any tests that have dependencies on data, do not make assumptions about any particular database or instance involved, and instead do the test data set up and teardown as part of the test suite.

## Features

Please refer to the specific packages documentation for more details.

### Asset management

Custom CSS and JavaScript files are merged and compressed using [Flask Assets](https://flask-assets.readthedocs.io/en/latest/) and [Webassets](https://webassets.readthedocs.io/en/latest/). This takes all `*.css` files in `app/static/src/css` and all `*.js` files in `app/static/src/js` and outputs a single compressed file to both `app/static/dist/css` and `app/static/dist/js` respectively.

CSS is [minified](https://en.wikipedia.org/wiki/Minification_(programming)) using [CSSMin](https://github.com/zacharyvoase/cssmin) and JavaScript is minified using [JSMin](https://github.com/tikitu/jsmin/). This removes all whitespace characters, comments and line breaks to reduce the size of the source code, making its transmission over a network more efficient.

### Cache busting

Merged and compressed assets are browser cache busted on update by modifying their URL with their MD5 hash using [Flask Assets](https://flask-assets.readthedocs.io/en/latest/) and [Webassets](https://webassets.readthedocs.io/en/latest/). The MD5 hash is appended to the file name, for example `custom-d41d8cd9.css` instead of a query string, to support certain older browsers and proxies that ignore the querystring in their caching behaviour.

### Forms generation and validation

Uses [Flask WTF](https://flask-wtf.readthedocs.io/en/stable/) and [WTForms](https://wtforms.readthedocs.io) to define and validate forms. Forms are rendered in your template using regular Jinja syntax.

### Form error handling

If a submitted form has any validation errors, an [error summary component](https://design-system.service.gov.uk/components/error-summary/) is shown at the top of the page, along with individual field [error messages](https://design-system.service.gov.uk/components/error-message/). This follows the GOV.UK Design System [validation pattern](https://design-system.service.gov.uk/patterns/validation/) and is built into the base page template.

### Flash messages

Messages created with Flask's `flash` function will be rendered using the GOV.UK Design System [notification banner component](https://design-system.service.gov.uk/components/notification-banner/). By default the blue "important" banner style will be used, unless a category of "success" is passed to use the green version.

### CSRF protection

Uses [Flask WTF](https://flask-wtf.readthedocs.io/en/stable/) to enable [Cross Site Request Forgery](https://en.wikipedia.org/wiki/Cross-site_request_forgery) protection per form and for the whole app.

CSRF errors are handled by creating a [flash message](#flash-messages) notification banner to inform the user that the form they submitted has expired.

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

### Rate limiting

Uses [Flask Limiter](https://flask-limiter.readthedocs.io/en/stable/) to set request rate limits on routes. The default rate limit is 2 requests per second _and_ 60 requests per minute (whichever is hit first) based on the client's remote IP address. Every time a request exceeds the rate limit, the view function will not get called and instead a [HTTP 429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) status will be returned.

Rate limit storage can be backed by [Redis](https://redis.io/) using the `RATELIMIT_STORAGE_URL` config value in `config.py`, or fall back to in-memory if not present. Rate limit information will also be added to various [response headers](https://flask-limiter.readthedocs.io/en/stable/#rate-limiting-headers).

## Support

This software is provided _"as-is"_ without warranty. Support is provided on a _"best endeavours"_ basis by the maintainers and open source community.

Please see the [contribution guidelines](CONTRIBUTING.md) for how to raise a bug report or feature request.
