# da-ayr-webapp
The webapp code for the Access Your Records (AYR) project.

This project consists of a Django application with a Postgres backend. Authentication and authorisation are handled
by Keyloack using Open ID Connect protocol.

# Running the app locally

### Environment variables

Some app configuration settings are loaded via environment variables. 
You need to create a `.env`file and add the following entries to it.

    
`SECRET_KEY=your-secret-key`

You can generate a secret-key with a password manage or a free online secret key generator service 
(e.g https://miniwebtool.com/django-secret-key-generator). 

Minimum length should be 50 chars. It should include alphanumeric values and symbols.

`KEYCLOACK_BASE_URI=http://kubernetes.docker.internal:8080`

`KEYCLOACK_REALM_NAME=ayr`

`OIDC_RP_CLIENT_ID=webapp`

`OIDC_RP_CLIENT_SECRET=your-client-secret`
This value needs to be copied from the Open ID Client created in Keycloack


`KEYCLOACK_DB_NAME=keycloack`

`KEYCLOACK_DB_USER=keycloack`

`KEYCLOACK_DB_PASSWORD=your-keycloack-db-password`

`KEYCLOAK_ADMIN=admin`

`KEYCLOAK_ADMIN_PASSWORD=your-keycloack-admin-password`

`WEBAPP_DB_NAME=django`

`WEBAPP_DB_USER=django`

`WEBAPP_DB_PASSWORD=yopur-webapp-db-password`

### Build and run

    make build

Alias for

    docker compose up --build

This will build and run the Django app available at `http://localhost:8000` and the Keycloack server available at `http://keycloack:8080`, alias for `http://localhost:8000`.
If you are running the app for the first time you will need to run migrations beforehand.

    make migrate

## Keycloack setup

Login to Keycloack using your admin credentials. 

From the admin panel create a new realm called `ayr`.

Once in the new realm (the default is called `admin`), create a new client with the following settings

`Client type = Open ID Connect`

`Client ID = webapp`

Fill the fields `Valid redirect URIs`, `Valid post logout redirect URIs`, `Web origins` with the value `http://localhost:8000/*`.

Set `Client authentication` to On. 

Save the changes.

Create a new user with email. In the credentials tab create a new password.

## Authentication flow

Navigate to http://localhost:8000.

Click on the `login` button. 

You will be redirected to keycloack for the authentication.
Enter the newly created user credentials and press enter. 

You should now be redirected to Django app index and see a `logout` button.

# Local Development
Create a new virtual environment for this project, then

    pip install pip-tools

See also Dependency Management section.

After installing `pip-tools`

    pip install -r requirements-dev.txt


# Dependency Management
 
This project is using [pip-tools](https://github.com/jazzband/pip-tools/) for dependency management. 

Install it in your local virtual env 

    pip install pip-tools

All dependencies should be declared and pinned in `pyproject.toml`

To generate a new `requirements.txt` file

    pip-compile -o requirements.txt pyproject.toml

To generate a new dev requirements.txt file

    pip-compile --extra dev -o requirements-dev.txt pyproject.toml
