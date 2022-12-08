# da-ayr-webapp
The webapp code for the Access Your Records (AYR) project

# Quickstart

Generate a .env file in the root directory
Add the following entry to the file
    SECRET_KEY=your-secret-key

You can generate a secret-key with a password manage or a free secret key generator services available online. Minimum length should be 50 chars. It should include alphanumeric values and symbols

    docker compose up --build

This will build and run the Django app available at http://localhost:8000/
