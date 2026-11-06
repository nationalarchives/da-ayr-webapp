FROM python:3.14.10-slim@sha256:af8a5aa14780025dbfbcfbc81bd8a91ebd87711dd5b0f48ed71090949dd7cb1d

WORKDIR /docker_app

# Install system dependencies including Node.js (cached layer)
RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    openssl \
    tesseract-ocr \
    antiword \
    unrtf \
    libreoffice \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (cached layer)
ENV POETRY_VIRTUALENVS_CREATE=false
RUN pip install --no-cache-dir poetry==2.4.1

# Copy Python dependency files first for better caching
COPY pyproject.toml poetry.lock /docker_app/
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-cache --without dev

# Copy Node.js dependency files and install
COPY package*.json /docker_app/
RUN npm ci

COPY build.sh /docker_app/build.sh
COPY app/ /docker_app/app
RUN chmod +x /docker_app/build.sh && /docker_app/build.sh && npm run build

COPY configs/ /docker_app/configs
COPY main_app.py .flaskenv /docker_app/
COPY local_services/mds_data_generator/ /docker_app/local_services/mds_data_generator/
COPY data_management/opensearch_indexer/requirements.txt /tmp/indexer-requirements.txt
RUN pip install --no-cache-dir -r /tmp/indexer-requirements.txt


ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

RUN openssl req -x509 -newkey rsa:2048 -nodes -out /docker_app/cert.pem -keyout /docker_app/key.pem -days 365 -subj '/C=GB/ST=Test/L=Test/O=Test/CN=localhost'

USER root

EXPOSE 5000

# Hit the unauthenticated index over the dev server's self-signed HTTPS.
# Uses Python (curl/wget are not in python:slim) and skips cert verification.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD ["python", "-c", "import ssl, urllib.request; urllib.request.urlopen('https://localhost:5000/', context=ssl._create_unverified_context(), timeout=4)"]

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
