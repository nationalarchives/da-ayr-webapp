# da-ayr-webapp
The webapp code for the Access Your Records (AYR) project

# Quickstart

Generate a .env file in the root directory
Add the following entry to the file
    SECRET_KEY=your-secret-key

You can generate a secret-key with a password manage or a free secret key generator services available online. Minimum length should be 50 chars. It should include alphanumeric values and symbols

    docker compose up --build

This will build and run the Django app available at http://localhost:8000/

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
