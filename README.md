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

### Set local environment variables

In the `.flaskenv` file you will find a number of environment variables. These are injected as global variables into the app and pre-populated into page templates as appropriate. Enter your specific information for the following:

- CONTACT_EMAIL
- CONTACT_PHONE
- DEPARTMENT_NAME
- DEPARTMENT_URL
- SERVICE_NAME
- SERVICE_PHASE
- SERVICE_URL

### Run app

```shell
flask run
```

You should now have the app running on <http://localhost:5000/>

## Testing

### Unit and Integration tests

To run the unit and integration tests you can run:

```shell
python -m pytest --cov=app --cov-report=term-missing --cov-branch -vvv
```

This also will generate a test coverage report.

### End To End Tests

We have a separate End To End suite of [Playwright](https://playwright.dev/python/docs/intro) tests in the `e2e_tests/` directory. These are also written in python and use the `pytest-playwright` `PyPi` package to run the tests as specified in the poetry depednecies.

In addition to installing the package, before you run the tests for the first time on your machine, you will need to run `playwright install` to install the required browsers for the end to end tests.

You can then run all of our Playwright tests against localhost with:

```shell
pytest e2e_tests/ --base-url=http://localhost:5000
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

- Forces all connections to `https`, unless running with debug enabled.
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
