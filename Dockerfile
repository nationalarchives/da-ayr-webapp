FROM python:3.10-slim-buster as build
EXPOSE 8000

# env vars
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# build libs
RUN apt update && apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib -y

# app deps
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

FROM python:3.10-slim-buster as run
WORKDIR /app
COPY --from=build /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY . /app
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]

FROM python:3.10-slim-buster as test
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --upgrade pip && pip install -r requirements-dev.txt --no-cache-dir