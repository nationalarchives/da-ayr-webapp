FROM python:3.10-slim-buster as build
EXPOSE 8000

# env vars
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# build libs
RUN apt update && apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib -y

# app deps
WORKDIR /code
COPY ./requirements.txt /code
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
COPY app/ /code/app
COPY project/ /code/project
COPY templates/ /code/templates
COPY manage.py /code

FROM build as test
COPY tests /code/tests
COPY requirements-dev.txt /code
COPY tests.sh /code
COPY tox.ini /code
COPY pyproject.toml /code
RUN pip install --upgrade pip && pip install -r requirements-dev.txt --no-cache-dir

FROM python:3.10-slim-buster as release
WORKDIR /code
COPY --from=build /code/ /code/
COPY --from=build /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=build /usr/local/bin/ /usr/local/bin/
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
