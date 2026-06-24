FROM python:3.13-slim@sha256:c33f0bc4364a6881bed1ec0cc2665e6c53c87a43e774aaeab88e6f17af105e4f

WORKDIR /docker_app

# Install system dependencies including Node.js (cached layer)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc=4:14.2.0-1 \
    libpq-dev=17.10-0+deb13u1 \
    openssl=3.5.6-1~deb13u2 \
    tesseract-ocr=5.5.0-1+b1 \
    antiword=0.37-17 \
    unrtf \
    libreoffice=4:25.2.3-2+deb13u5 \
    nodejs=20.19.2+dfsg-1+deb13u2 \
    npm=9.2.0~ds1-3 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (cached layer)
ENV POETRY_VIRTUALENVS_CREATE=false
RUN pip install --no-cache-dir poetry==2.4.1

# Copy Python dependency files first for better caching
COPY pyproject.toml poetry.lock /docker_app/
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-cache

# Copy Node.js dependency files and install
COPY package*.json /docker_app/
RUN npm ci
COPY app/static/src/scss /docker_app/app/static/src/scss
# Build CSS files before copying the rest of the app as
# we won't update them as often as other source files
RUN npm run build

# Preserve CSS files as copying app directory will overwrite them
RUN cp -r /docker_app/app/static/src/css /tmp/css_backup
COPY app/ /docker_app/app
COPY configs/ /docker_app/configs
COPY main_app.py .flaskenv /docker_app/
COPY local_services/mds_data_generator/ /docker_app/local_services/mds_data_generator/
COPY data_management/opensearch_indexer/requirements.txt /tmp/indexer-requirements.txt
RUN pip install --no-cache-dir -r /tmp/indexer-requirements.txt
# Restore the built CSS files
RUN cp -r /tmp/css_backup /docker_app/app/static/src/css


ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

RUN openssl req -x509 -newkey rsa:2048 -nodes -out /docker_app/cert.pem -keyout /docker_app/key.pem -days 365 -subj '/C=GB/ST=Test/L=Test/O=Test/CN=localhost'

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /docker_app
USER appuser

EXPOSE 5000

# Hit the unauthenticated index over the dev server's self-signed HTTPS.
# Uses Python (curl/wget are not in python:slim) and skips cert verification.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD ["python", "-c", "import ssl, urllib.request; urllib.request.urlopen('https://localhost:5000/', context=ssl._create_unverified_context(), timeout=4)"]

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
