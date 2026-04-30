# Python 3.13-slim
FROM python@sha256:0ba001803c72c128063cfa88863755f905cefabe73c026c66a5a86d8f1d63e98

WORKDIR /docker_app

# Install system dependencies including Node.js (cached layer)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    openssl \
    curl \
    tesseract-ocr \
    antiword \
    unrtf \
    libreoffice \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (cached layer)
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

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

EXPOSE 5000

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
